import logging
import sys
from pathlib import Path

LOG_DIR = Path(__file__).parents[1] / ".logs"
LOG_DIR.mkdir(exist_ok=True)

_loggers: dict[str, logging.Logger] = {}


def get_thread_logger(thread_ts: str) -> logging.Logger:
    """Get a logger that writes to both stdout and a per-thread log file."""
    if thread_ts in _loggers:
        return _loggers[thread_ts]

    logger = logging.getLogger(f"thread.{thread_ts}")
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    formatter = logging.Formatter("%(asctime)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

    # File handler — one file per thread
    fh = logging.FileHandler(LOG_DIR / f"{thread_ts}.log")
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    # Stdout handler — use stdout to separate from slack_bolt's stderr logging
    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(formatter)
    logger.addHandler(sh)

    _loggers[thread_ts] = logger
    return logger
