# agents/tools.py
"""Agent tools — wrappers for external service calls.

This module demonstrates the tool wrapper pattern:
- Each tool wraps an external service call (MCP, API, etc.)
- Input/output security gates are applied consistently
- Error handling is centralized

To add new tools:
1. Define a new @tool function
2. Call MCP_CLIENT (or your service client)
3. Apply security checks
4. Add to TOOLS registry
"""

from langchain_core.tools import tool

from utils.logger import LOGGER
from utils.mcp_client import MCP_CLIENT
from utils.security import check_input, check_output


def _block_error(reason: str) -> str:
    """Format a blocked request error message."""
    return f"[BLOCKED] {reason}"


# ── Example Tools ────────────────────────────────────────────────────────────
# These demonstrate the pattern. Replace with your own tools.


@tool
async def execute_query(query: str) -> str:
    """Execute a query against an external service.

    Args:
        query: The query string to execute.
    """
    safe = check_input(query)
    if safe.is_blocked:
        return _block_error(safe.reason)
    try:
        client = await MCP_CLIENT.get_client()
        result = await client.tool_execute({"query": safe.sanitized_text})
        safe_out = check_output(result)
        if safe_out.is_blocked:
            return _block_error(safe_out.reason)
        return safe_out.sanitized_text
    except Exception as e:
        LOGGER.error("execute_query failed", exc_info=True)
        return f"Error: {e}"


@tool
async def fetch_resource(resource_id: str) -> str:
    """Fetch a resource by ID from an external service.

    Args:
        resource_id: The unique identifier of the resource.
    """
    safe = check_input(resource_id)
    if safe.is_blocked:
        return _block_error(safe.reason)
    try:
        client = await MCP_CLIENT.get_client()
        result = await client.tool_fetch({"id": safe.sanitized_text})
        safe_out = check_output(result)
        if safe_out.is_blocked:
            return _block_error(safe_out.reason)
        return safe_out.sanitized_text
    except Exception as e:
        LOGGER.error("fetch_resource failed", exc_info=True)
        return f"Error: {e}"


# ── Tool registry ────────────────────────────────────────────────────────────
# Add your tools here. The order determines execution priority.
TOOLS = [
    execute_query,
    fetch_resource,
    # read_file,
    # list_directory,
    # search_files,
    # search_web,
    # fetch_url,
    # write_file,
    # create_directory,
    # rename_file,
]
