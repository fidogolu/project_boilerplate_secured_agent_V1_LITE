# Production-Ready AI Agent Boilerplate

> A modular, production-grade template for building secured AI agents with ReAct loop orchestration via LangGraph, MCP client integration, and comprehensive security gates.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Type: typing](https://img.shields.io/badge/typing-Annotated%20%7C%20TypedDict-green.svg)](https://docs.python.org/3/library/typing.html)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE.md)

---

## 📖 Description

**AI Agent Boilerplate** is a technology-agnostic framework designed as a reusable template for building **production-grade AI agents**. It implements a complete architecture stack including:

- **ReAct Agent Loop** orchestrated by LangGraph with built-in input/output security gates
- **MCP Client** implementing JSON-RPC 2.0 over HTTP with SSE response parsing
- **Tool wrappers** bridging LangChain `@tool` decorators to external service endpoints
- **Modular architecture** with clear separation of concerns across agents, tools, utilities, and configuration layers
- **Observability** integration for tracing and monitoring

This boilerplate is designed to be adapted to any external service or tool-calling protocol.

---

## ✨ Key Features

### Architecture & Design Patterns

| Feature | Description |
|---------|-------------|
| **Clean Architecture** | Separation of concerns between agents, tools, utilities, and configuration layers |
| **ReAct Pattern** | LangGraph-based state machine implementing the Reason-Act loop |
| **Singleton Pattern** | Thread-safe singleton for MCP client (`MCP_CLIENT`) |
| **Async Context Manager** | Proper lifecycle management (`__aenter__`/`__aexit__`) |
| **State Management** | `TypedDict` + `Annotated` types for LangGraph state with reducers |

### Security

| Feature | Description |
|---------|-------------|
| **Input/Output Sanitization** | `check_input()` and `check_output()` with `SecurityResult` dataclass |
| **Configurable Security Modes** | Switch between `none`, `lite`, `full`, or `remote` via `SECURITY_MODE` env var |
| **Security Layer Stub** | Ready-to-replace security module (`utils/security.py`) |

### Developer Experience

| Feature | Description |
|---------|-------------|
| **Strict Types** | Python `TypedDict` + `Annotated` types for LangGraph state management |
| **Structured Logging** | Production-ready logger with console and file handlers (`utils/logger.py`) |
| **Configuration Management** | Single source of truth via `config/constants.py` |
| **uv Package Management** | Fast, dependency-resolved Python environment via `pyproject.toml` |

---

## 🏗️ Architecture & Design Patterns

```mermaid
graph TD
    subgraph UI["User Interface"]
        Gradio["Gradio ChatInterface<br/>port 7860"]
    end

    subgraph Agent["Agent Orchestration LangGraph StateGraph"]
        CI["check_input Security Gate In"]
        LLM["call_llm LLM Tool Binding"]
        Tools["ToolNode LangChain"]
        CO["check_output Security Gate Out"]
    end

    subgraph ToolsLayer["Tools Layer"]
        T1["execute_query"]
        T2["fetch_resource"]
    end

    subgraph Client["MCP Client Singleton"]
        HTTP["httpx.AsyncClient JSON-RPC 2.0"]
    end

    subgraph External["External Services"]
        S1["tool_execute"]
        S2["tool_fetch"]
    end

    subgraph LLMSvc["LLM Service"]
        Model["ChatOpenAI OpenAI-compatible"]
    end

    UI -->|"user_message"| CI
    CI --> LLM
    LLM -->|"tool_calls"| Tools
    Tools -->|"results"| LLM
    LLM -->|"final"| CO
    CO -->|"response"| UI

    Tools --> HTTP
    HTTP --> S1
    HTTP --> S2

    LLM --> Model
    Model -.|"response"| LLM
```

### Technical Stack

| Category | Technology |
|----------|-----------|
| **Agent Framework** | LangGraph, LangChain |
| **Protocol** | httpx async, JSON-RPC 2.0 over HTTP |
| **LLM Backend** | ChatOpenAI OpenAI-compatible API |
| **UI** | Gradio ChatInterface |
| **Observability** | Langfuse configurable |
| **Package Manager** | uv |

---

## 🚀 How to Use

### Prerequisites

- Python 3.10 – 3.13
- [uv](https://github.com/astral-sh/uv) — Python package manager: `pip install uv`

### Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/<your-username>/mcp-agent-boilerplate.git
cd mcp-agent-boilerplate

# 2. Create a virtual environment and install dependencies
uv sync

# 3. Configure environment variables
cp .env.example .env
# Edit .env with your LLM endpoint, service URLs, and security settings

# 4. Run the agent
uv run python main.py
```

The Gradio interface will be available at `http://localhost:7860`.

### Project Structure

```
mcp-agent-boilerplate/
├── main.py                    # Entry point Gradio UI + agent invocation
├── pyproject.toml             # Dependencies & uv configuration
├── .env.example               # Environment variable template
├── README.md                  # This file
├── LICENSE.md                 # MIT License
│
├── agents/                    # Agent core components
│   ├── graph.py               # LangGraph StateGraph ReAct loop
│   ├── state.py               # AgentState TypedDict
│   └── tools.py               # MCP tool wrappers
│
├── config/                    # Configuration layer
│   └── constants.py           # Single source of truth env vars
│
├── utils/                     # Utility modules
│   ├── llm.py                 # LLM worker singleton
│   ├── logger.py              # Logging configuration
│   ├── mcp_client.py          # Async HTTP client JSON-RPC over HTTP
│   ├── security.py            # Security scanners SecurityResult
│   └── preprocessing.py       # Text preprocessing utilities
│
├── tests/                     # Test suite
│   └── test_security.py       # Security layer unit tests
│
└── docs/
    └── architecture.mermaid   # Architecture diagram
```

---

## 🧪 Testing

```bash
# Run all tests
uv run pytest

# Verbose output
uv run pytest -v

# Security tests only
uv run pytest tests/test_security.py -v
```

---

## ⚙️ Configuration

All configuration is managed through environment variables. See [`.env.example`](.env.example) for the full list.

### Key Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `WORKER_LLM_URL` | LLM API endpoint | `http://localhost:8000/v1` |
| `WORKER_MODEL_NAME` | Model to use | `your-model-name` |
| `MCP_BASE_URL` | External service base URL | `http://localhost:8080` |
| `SECURITY_MODE` | Security scanning mode | `lite` |
| `LOG_LEVEL` | Logging verbosity | `INFO` |
| `MAX_MESSAGE_LENGTH` | Max input message length | `4096` |

### Security Modes

| Mode | Description | Use Case |
|------|-------------|----------|
| `none` | No security checks | Local development |
| `lite` | Basic sanitization, no GPU | Development |
| `full` | All scanners + GPU models | Production single-host |
| `remote` | HTTP call to security service | Production multi-host |

---

## 🛠️ Extending the Boilerplate

### Adding a New Tool

```python
# agents/tools.py
@tool
async def my_custom_tool(param: str) -> str:
    """Describe your tool's purpose."""
    safe = check_input(param)
    if safe.is_blocked:
        return _block_error(safe.reason)
    try:
        client = await MCP_CLIENT.get_client()
        result = await client.my_custom_method(safe.sanitized_text)
        safe_out = check_output(result)
        if safe_out.is_blocked:
            return _block_error(safe_out.reason)
        return safe_out.sanitized_text
    except Exception as e:
        LOGGER.error("my_custom_tool failed", exc_info=True)
        return f"Error: {e}"

# Register in TOOLS list
TOOLS = [my_custom_tool, ...]
```

### Replacing the Security Layer

Replace `utils/security.py` with your own implementation. The interface is:

```python
@dataclass
class SecurityResult:
    is_blocked: bool
    reason: str = ""
    sanitized_text: str = ""

def check_input(text: str, source: str = "unknown") -> SecurityResult:
    ...

def check_output(text: str, prompt: str = "", source: str = "unknown") -> SecurityResult:
    ...
```

---

## 📄 License

This project is licensed under the [MIT License](LICENSE.md).

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

**Built with** ⚡ by [Your Name](https://github.com/your-username)
