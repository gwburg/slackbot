import traceback
from datetime import datetime, timezone
from pathlib import Path

from bot.app import app
from bot.llm import run_agent
from bot.slack_utils import add_reaction, fetch_thread_messages, get_bot_user_id, remove_reaction
from bot.threads import get_thread_lock, is_active_thread, track_thread

_LOG_DIR = Path.home() / ".local" / "share" / "slackbot" / "logs"
_LOG_DIR.mkdir(exist_ok=True)


def _log_error(thread_ts, exc_text):
    log_path = _LOG_DIR / f"{thread_ts}.log"
    timestamp = datetime.now(timezone.utc).isoformat()
    with log_path.open("a") as f:
        f.write(f"[{timestamp}]\n{exc_text}\n")


@app.event("app_mention")
def handle_mention(event, say):
    channel = event["channel"]
    ts = event["ts"]
    thread_ts = event.get("thread_ts", ts)
    track_thread(thread_ts)

    lock = get_thread_lock(thread_ts)
    with lock:
        add_reaction(channel, ts)
        try:
            messages = fetch_thread_messages(channel, thread_ts)
            run_agent(messages, {"channel": channel, "thread_ts": thread_ts})
        except Exception:
            _log_error(thread_ts, traceback.format_exc())
        finally:
            remove_reaction(channel, ts)


@app.event("message")
def handle_message(event, say):
    if event.get("subtype"):
        return
    uid = get_bot_user_id()
    if f"<@{uid}>" in event.get("text", ""):
        return  # handled by app_mention

    thread_ts = event.get("thread_ts")
    if not thread_ts or not is_active_thread(thread_ts):
        return

    channel = event["channel"]
    ts = event["ts"]
    lock = get_thread_lock(thread_ts)

    with lock:
        add_reaction(channel, ts)
        try:
            messages = fetch_thread_messages(channel, thread_ts)
            run_agent(messages, {"channel": channel, "thread_ts": thread_ts})
        except Exception:
            _log_error(thread_ts, traceback.format_exc())
        finally:
            remove_reaction(channel, ts)
