import os

from dotenv import load_dotenv

load_dotenv()

from bot.app import app  # noqa: E402
import bot.handlers  # noqa: E402, F401
from slack_bolt.adapter.socket_mode import SocketModeHandler  # noqa: E402

if __name__ == "__main__":
    handler = SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    handler.start()
