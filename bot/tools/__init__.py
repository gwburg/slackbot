"""Tool registry - aggregates all tool modules."""

import json

from bot.tools import bash, files, web

_MODULES = [bash, files, web]

TOOL_DEFINITIONS = [defn for m in _MODULES for defn in m.DEFINITIONS]

_TOOL_MAP = {
    defn["function"]["name"]: m
    for m in _MODULES
    for defn in m.DEFINITIONS
}


def execute_tool(name, arguments, context):
    """Execute a tool call and return the result string."""
    try:
        args = json.loads(arguments) if isinstance(arguments, str) else arguments
    except json.JSONDecodeError as e:
        return f"Error parsing arguments: {e}"

    module = _TOOL_MAP.get(name)
    if module is None:
        return f"Unknown tool: {name}"
    return module.execute(name, args, context)
