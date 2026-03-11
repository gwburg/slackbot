import json

from bot.app import llm
from bot.config import MODEL, SYSTEM_PROMPT
from bot.logging import get_thread_logger
from bot.tools import TOOL_DEFINITIONS, execute_tool

MAX_ITERATIONS = 10


def _log_messages(log, messages):
    """Log all user/assistant messages in the conversation history."""
    for msg in messages:
        role = msg.get("role", "?")
        if role == "system":
            continue
        content = msg.get("content", "")
        log.info("[%s] %s", role, content)


def run_agent(messages, context):
    """Run the agentic loop: call the LLM, execute tool calls, repeat."""
    thread_ts = context.get("thread_ts", "?")
    log = get_thread_logger(thread_ts)
    log.info("=== run_agent starting | messages=%d ===", len(messages))

    _log_messages(log, messages)

    chat_messages = [{"role": "system", "content": SYSTEM_PROMPT}, *messages]

    for i in range(MAX_ITERATIONS):
        kwargs = {"model": MODEL, "messages": chat_messages}
        if TOOL_DEFINITIONS:
            kwargs["tools"] = TOOL_DEFINITIONS
        log.info("--- LLM call iter=%d | model=%s ---", i, MODEL)
        response = llm.chat.completions.create(**kwargs)
        choice = response.choices[0]
        text = choice.message.content or ""

        log.info("finish_reason=%s", choice.finish_reason)
        if text:
            log.info("[assistant] %s", text)

        if choice.finish_reason == "tool_calls":
            chat_messages.append(choice.message)
            for tool_call in choice.message.tool_calls:
                args = tool_call.function.arguments
                log.info("[tool_call] %s(%s)", tool_call.function.name, args)
                result = execute_tool(
                    tool_call.function.name,
                    args,
                    context,
                )
                log.info("[tool_result] %s -> %s", tool_call.function.name, result)
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
            log.info("=== done ===")
            return

    log.warning("=== hit max iterations (%d) ===", MAX_ITERATIONS)
