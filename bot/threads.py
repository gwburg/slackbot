import json
import threading
from pathlib import Path

MEMORY_DIR = Path.home() / ".local" / "share" / "slackbot" / "memory"
MEMORY_DIR.mkdir(exist_ok=True)
ACTIVE_THREADS_FILE = MEMORY_DIR / "active_threads.json"

_lock = threading.Lock()
_thread_locks: dict[str, threading.Lock] = {}


def load_active_threads():
    if ACTIVE_THREADS_FILE.exists():
        return set(json.loads(ACTIVE_THREADS_FILE.read_text()))
    return set()


def save_active_threads(threads):
    ACTIVE_THREADS_FILE.write_text(json.dumps(list(threads)))


active_threads = load_active_threads()


def track_thread(thread_ts):
    active_threads.add(thread_ts)
    save_active_threads(active_threads)


def is_active_thread(thread_ts):
    return thread_ts in active_threads


def get_thread_lock(thread_ts):
    """Get a per-thread lock to prevent concurrent responses in the same thread."""
    with _lock:
        if thread_ts not in _thread_locks:
            _thread_locks[thread_ts] = threading.Lock()
        return _thread_locks[thread_ts]
