from bot.app import llm
from bot.config import MODEL, SYSTEM_PROMPT
from bot.logging import get_thread_logger
from bot.tools import TOOL_DEFINITIONS, execute_tool

MAX_ITERATIONS = 10


def run_agent(messages, context):
    """Run the agentic loop: call the LLM, execute tool calls, repeat."""
    thread_ts = context.get("thread_ts", "?")
    log = get_thread_logger(thread_ts)
    log.info("starting | messages=%d", len(messages))

    chat_messages = [{"role": "system", "content": SYSTEM_PROMPT}, *messages]

    for i in range(MAX_ITERATIONS):
        kwargs = {"model": MODEL, "messages": chat_messages}
        if TOOL_DEFINITIONS:
            kwargs["tools"] = TOOL_DEFINITIONS
        response = llm.chat.completions.create(**kwargs)
        choice = response.choices[0]
        text = choice.message.content or ""
        log.info("iter=%d | finish_reason=%s | text=%r", i, choice.finish_reason, text[:200])

        if choice.finish_reason == "tool_calls":
            chat_messages.append(choice.message)
            for tool_call in choice.message.tool_calls:
                log.info("  tool=%s | args=%s", tool_call.function.name, tool_call.function.arguments[:200])
                result = execute_tool(
                    tool_call.function.name,
                    tool_call.function.arguments,
                    context,
                )
                log.info("  result=%s", result[:200])
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
            log.info("done")
            return

    log.warning("hit max iterations (%d)", MAX_ITERATIONS)
