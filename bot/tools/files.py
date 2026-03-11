"""File editing tools - read, write, and edit files."""

from pathlib import Path

DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read and return the contents of a file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "The file path to read.",
                    },
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Create or overwrite a file with the given content.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "The file path to write.",
                    },
                    "content": {
                        "type": "string",
                        "description": "The content to write to the file.",
                    },
                },
                "required": ["path", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "str_replace_in_file",
            "description": "Replace an exact string in a file with new text. The old_str must match exactly (including whitespace and indentation).",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "The file path to edit.",
                    },
                    "old_str": {
                        "type": "string",
                        "description": "The exact string to replace.",
                    },
                    "new_str": {
                        "type": "string",
                        "description": "The replacement string.",
                    },
                },
                "required": ["path", "old_str", "new_str"],
            },
        },
    },
]


def execute(name, args, context):
    if name == "read_file":
        return _read_file(args["path"])
    elif name == "write_file":
        return _write_file(args["path"], args["content"])
    elif name == "str_replace_in_file":
        return _str_replace_in_file(args["path"], args["old_str"], args["new_str"])


def _read_file(path):
    try:
        return Path(path).read_text()
    except Exception as e:
        return f"Error reading file: {e}"


def _write_file(path, content):
    try:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content)
        return f"Wrote {len(content)} bytes to {path}"
    except Exception as e:
        return f"Error writing file: {e}"


def _str_replace_in_file(path, old_str, new_str):
    try:
        p = Path(path)
        content = p.read_text()
        if old_str not in content:
            return f"Error: old_str not found in {path}"
        p.write_text(content.replace(old_str, new_str, 1))
        return f"Successfully replaced text in {path}"
    except Exception as e:
        return f"Error editing file: {e}"
