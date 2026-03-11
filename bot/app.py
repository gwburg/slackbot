import logging
import os

from openai import OpenAI
from slack_bolt import App

app = App(token=os.environ["SLACK_BOT_TOKEN"], log_level=logging.WARNING)

llm = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ["OPENROUTER_API_KEY"],
)
