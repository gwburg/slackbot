from bot.app import llm
from bot.config import MODEL, SHOULD_RESPOND_PROMPT, SYSTEM_PROMPT
from bot.slack_utils import send_message


def get_response(messages, channel, thread_ts):
    """Generate an LLM response and send it to Slack."""
    response = llm.chat.completions.create(
        model=MODEL,
        messages=[{"role": "system", "content": SYSTEM_PROMPT}, *messages],
    )
    text = response.choices[0].message.content
    send_message(channel, text, thread_ts=thread_ts)
    return text


def should_respond(messages):
    """Ask the LLM whether it should respond to the latest thread message."""
    # Flatten the conversation into a single block so the LLM doesn't
    # treat it as a conversation to continue
    conversation = "\n".join(
        f"{'[You]' if m['role'] == 'assistant' else '[User]'}: {m['content']}"
        for m in messages
    )
    prompt = f"{SHOULD_RESPOND_PROMPT}\n\n<conversation>\n{conversation}\n</conversation>"
    response = llm.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=10,
    )
    decision = response.choices[0].message.content.strip().upper()
    return "RESPOND" in decision, decision
