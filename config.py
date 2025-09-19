import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
TARGET_CHAT_ID = os.getenv("TARGET_CHAT_ID")
START_FEED_CHAT_ID = os.getenv("START_FEED_CHAT_ID")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден в .env")
if not TARGET_CHAT_ID:
    raise ValueError("TARGET_CHAT_ID не найден в .env")

TARGET_CHAT_ID = int(TARGET_CHAT_ID)

if START_FEED_CHAT_ID:
    try:
        START_FEED_CHAT_ID = int(START_FEED_CHAT_ID)
    except ValueError:
        START_FEED_CHAT_ID = None
