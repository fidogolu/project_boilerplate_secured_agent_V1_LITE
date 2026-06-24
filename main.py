# main.py
"""Gradio chat interface — entry point.

Calls the LangGraph ReAct agent and streams the response to the user.

This module demonstrates:
1. Input validation (length check)
2. Structured logging via LOGGER
3. Async agent invocation pattern
"""

import gradio as gr
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage

from agents.graph import graph
from config.constants import MAX_MESSAGE_LENGTH
from utils.logger import LOGGER

load_dotenv()


async def chat(user_message: str, history: list) -> str:
    """Handle a user message and return the agent's response.

    Args:
        user_message: The user's input text.
        history: Conversation history (list of [user, assistant] pairs).

    Returns:
        The agent's response text.
    """

    # ── Input Validation ────────────────────────────────────────────────────
    if not user_message or not user_message.strip():
        return ""

    max_len = MAX_MESSAGE_LENGTH
    if len(user_message) > max_len:
        LOGGER.warning(
            "Message too long: %d > %d characters",
            len(user_message),
            max_len,
        )
        msg = f"Error: Message exceeds max length of {max_len} characters"
        return msg

    # ── Log Request ─────────────────────────────────────────────────────────
    LOGGER.info("User message received")

    try:
        result = await graph.ainvoke(
            {
                "messages": [HumanMessage(content=user_message)],
                "final_response": None,
                "error": None,
            }
        )
    except Exception as e:
        LOGGER.error("graph.ainvoke failed", exc_info=True)
        return f"Unexpected error: {e}"

    if result.get("error"):
        LOGGER.warning("Agent returned error: %s", result["error"])
        return f"Error: {result['error']}"

    response = result.get("final_response") or "No response generated."
    LOGGER.info("Response generated successfully")

    return response


def create_demo():
    """Create Gradio demo interface."""
    with gr.Blocks(title="AI Agent Playground") as demo:
        gr.Markdown("## AI Agent Playground")
        gr.Markdown(
            "Ask your questions — interact with an AI agent\n" "powered by LangGraph."
        )

        _demo = gr.ChatInterface(
            fn=chat,
            examples=[
                "What is the capital of France?",
                "Search for information about AI",
                "Help me understand this concept",
            ],
        )

    return demo


demo = create_demo()

# Launch the Gradio interface
demo.launch(server_name="0.0.0.0", server_port=7860)
