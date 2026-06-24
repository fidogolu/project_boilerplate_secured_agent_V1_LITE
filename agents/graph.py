# agents/graph.py
"""ReAct agent — LangGraph graph definition.

Architecture:
    user_message -> [security_check_in] -> call_llm -> [tool_execution]
    -> call_llm -> ... -> [security_check_out] -> response

This module demonstrates:
- StateGraph-based ReAct loop orchestration
- Conditional routing based on LLM tool calls
- Input/output security gates
- Error propagation through agent state
"""

from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import END, StateGraph
from langgraph.prebuilt import ToolNode

from agents.state import AgentState
from agents.tools import TOOLS
from utils.llm import WORKER_LLM
from utils.logger import LOGGER
from utils.security import check_input, check_output

# System prompt — customize for your specific use case
_SYSTEM_PROMPT = """You are a helpful assistant with access to external tools.

Use the appropriate tools to answer the user's request.
Always think step by step before calling a tool.
When you have enough information, provide a clear and concise final answer.
"""

# Bind tools to LLM
_llm_with_tools = WORKER_LLM.bind_tools(TOOLS)


# ── Nodes ────────────────────────────────────────────────────────────────────


async def check_input_node(state: AgentState) -> dict:
    """Apply security validation on the latest user message."""
    if state.get("error"):
        return {}

    last_msg = state["messages"][-1]
    if hasattr(last_msg, "content"):
        text = last_msg.content
    else:
        text = str(last_msg)

    safe = check_input(text)
    if safe.is_blocked:
        LOGGER.warning("Input blocked: %s", safe.reason)
        return {"error": f"Input blocked: {safe.reason}"}

    return {"messages": [HumanMessage(content=safe.sanitized_text)]}


async def call_llm(state: AgentState) -> dict:
    """Call the LLM with the current message history."""
    if state.get("error"):
        return {}

    messages = [SystemMessage(content=_SYSTEM_PROMPT)] + state["messages"]

    try:
        response = await _llm_with_tools.ainvoke(messages)
        tool_calls = getattr(response, "tool_calls", []) or []
        LOGGER.debug("LLM response: tool_calls=%d", len(tool_calls))
        return {"messages": [response]}
    except Exception as e:
        LOGGER.error("LLM call failed", exc_info=True)
        return {"error": str(e)}


async def check_output_node(state: AgentState) -> dict:
    """Apply security validation on the LLM final response."""
    if state.get("error"):
        return {}

    last_msg = state["messages"][-1]
    if hasattr(last_msg, "content"):
        text = last_msg.content
    else:
        text = str(last_msg)

    safe = check_output(text)
    if safe.is_blocked:
        LOGGER.warning("Output blocked: %s", safe.reason)
        return {"error": f"Output blocked: {safe.reason}"}

    return {"final_response": safe.sanitized_text}


# ── Conditional edge ─────────────────────────────────────────────────────────


def should_use_tools(state: AgentState) -> str:
    """Route to tools if the LLM made tool calls, otherwise finalize."""
    last_msg = state["messages"][-1]
    if hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
        return "tools"
    return END


# ── Build graph ──────────────────────────────────────────────────────────────

workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("check_input", check_input_node)
workflow.add_node("call_llm", call_llm)
workflow.add_node("tools", ToolNode(TOOLS))
workflow.add_node("check_output", check_output_node)

# Set entry and edges
workflow.set_entry_point("check_input")
workflow.add_conditional_edges(
    "call_llm",
    should_use_tools,
    {
        "tools": "tools",
        END: "check_output",
    },
)
workflow.add_edge("check_input", "call_llm")
workflow.add_edge("tools", "call_llm")
workflow.add_edge("check_output", END)

graph = workflow.compile()
