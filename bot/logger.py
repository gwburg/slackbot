import logging
from datetime import UTC, datetime
from pathlib import Path

LOG_DIR = Path.home() / ".local" / "share" / "slackbot" / "logs"
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

    dt = datetime.fromtimestamp(float(thread_ts), tz=UTC).strftime("%Y-%m-%d_%H-%M-%S")
    fh = logging.FileHandler(LOG_DIR / f"{dt}.log")
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    _loggers[thread_ts] = logger
    return logger
