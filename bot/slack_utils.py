from datetime import UTC, datetime

from bot.app import app
from bot.config import BOT_NAME

_bot_user_id = None
_user_name_cache = {}


def get_bot_user_id():
    global _bot_user_id
    if _bot_user_id is None:
        _bot_user_id = app.client.auth_test()["user_id"]
    return _bot_user_id


def resolve_user_name(user_id):
    if user_id not in _user_name_cache:
        try:
            result = app.client.users_info(user=user_id)
            profile = result["user"]["profile"]
            _user_name_cache[user_id] = profile.get("display_name") or profile.get("real_name") or user_id
        except Exception:
            _user_name_cache[user_id] = user_id
    return _user_name_cache[user_id]


def format_timestamp(ts):
    return datetime.fromtimestamp(float(ts), tz=UTC).strftime("%Y-%m-%d %H:%M:%S UTC")


def fetch_thread_messages(channel, thread_ts):
    """Fetch all messages in a thread and convert to chat format."""
    try:
        result = app.client.conversations_replies(channel=channel, ts=thread_ts)
    except Exception:
        return []
    messages = []
    uid = get_bot_user_id()
    for msg in result["messages"]:
        if msg.get("subtype"):
            continue
        text = msg.get("text", "")
        ts = msg.get("ts", "")
        # Replace raw bot mention with readable name
        text = text.replace(f"<@{uid}>", f"@{BOT_NAME}")
        if msg.get("user") == uid:
            messages.append({"role": "assistant", "content": text})
        else:
            user_id = msg.get("user", "unknown")
            name = resolve_user_name(user_id)
            timestamp = format_timestamp(ts)
            messages.append({"role": "user", "content": f"[{timestamp}] {name}: {text}"})
    return messages


def add_reaction(channel, timestamp, emoji="memo"):
    """Add an emoji reaction to a message."""
    try:
        app.client.reactions_add(channel=channel, timestamp=timestamp, name=emoji)
    except Exception:
        pass  # best-effort


def remove_reaction(channel, timestamp, emoji="memo"):
    """Remove an emoji reaction from a message."""
    try:
        app.client.reactions_remove(channel=channel, timestamp=timestamp, name=emoji)
    except Exception:
        pass  # best-effort


def send_message(channel, text, thread_ts=None):
    """Send a message to a Slack channel or thread. Single path for all outgoing messages."""
    app.client.chat_postMessage(channel=channel, text=text, thread_ts=thread_ts)
