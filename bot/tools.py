"""Tool definitions and execution for the agentic loop."""

import json

TOOL_DEFINITIONS = []


def execute_tool(name, arguments, context):
    """Execute a tool call and return the result string.

    context is a dict with keys like 'channel' and 'thread_ts'
    that tools may need.
    """
    return f"Unknown tool: {name}"
