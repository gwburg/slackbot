import json
from pathlib import Path

from bot.app import llm
from bot.config import MODEL, SYSTEM_PROMPT
from bot.tools import TOOL_DEFINITIONS, execute_tool

MAX_ITERATIONS = 10

_HISTORY_DIR = Path.home() / ".local" / "share" / "slackbot" / "history"
_HISTORY_DIR.mkdir(exist_ok=True)


def _history_path(thread_ts):
    return _HISTORY_DIR / f"{thread_ts}.json"


def _load_history(thread_ts):
    path = _history_path(thread_ts)
    if path.exists():
        return json.loads(path.read_text())
    return None


def _save_history(thread_ts, messages):
    _history_path(thread_ts).write_text(json.dumps(messages))


def _build_chat_messages(thread_ts, slack_messages):
    """Merge persisted history (with tool calls) with new Slack messages."""
    persisted = _load_history(thread_ts)
    if not persisted:
        return [{"role": "system", "content": SYSTEM_PROMPT}, *slack_messages]

    known_contents = {
        msg["content"]
        for msg in persisted
        if isinstance(msg.get("content"), str)
    }
    new_messages = [m for m in slack_messages if m.get("content") not in known_contents]
    return [{"role": "system", "content": SYSTEM_PROMPT}, *persisted, *new_messages]


def run_agent(messages, context):
    """Run the agentic loop: call the LLM, execute tool calls, repeat."""
    thread_ts = context.get("thread_ts", "?")
    chat_messages = _build_chat_messages(thread_ts, messages)

    for i in range(MAX_ITERATIONS):
        kwargs = {"model": MODEL, "messages": chat_messages}
        if TOOL_DEFINITIONS:
            kwargs["tools"] = TOOL_DEFINITIONS
        response = llm.chat.completions.create(**kwargs)
        choice = response.choices[0]
        text = choice.message.content or ""

        if choice.finish_reason == "tool_calls":
            chat_messages.append(choice.message)
            for tool_call in choice.message.tool_calls:
                result = execute_tool(
                    tool_call.function.name,
                    tool_call.function.arguments,
                    context,
                )
                chat_messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": result,
                    }
                )
        else:
            if text:
                from bot.slack_utils import send_message
                send_message(context["channel"], text, thread_ts=context["thread_ts"])
            _save_history(thread_ts, chat_messages[1:])  # exclude system prompt
            return
