import traceback

from bot.app import app
from bot.llm import run_agent
from bot.slack_utils import add_reaction, fetch_thread_messages, get_bot_user_id, remove_reaction
from bot.threads import get_thread_lock, is_active_thread, track_thread


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
            traceback.print_exc()
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
            traceback.print_exc()
        finally:
            remove_reaction(channel, ts)
