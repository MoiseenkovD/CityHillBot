import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
TARGET_CHAT_ID = os.getenv("TARGET_CHAT_ID")  # дефолтный чат (fallback)
START_FEED_CHAT_ID = os.getenv("START_FEED_CHAT_ID")

# новые: отдельные чаты для потоков
TARGET_CHAT_ID_SLAVIC = os.getenv("TARGET_CHAT_ID_SLAVIC")
TARGET_CHAT_ID_HYBRID = os.getenv("TARGET_CHAT_ID_HYBRID")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден в .env")
if not TARGET_CHAT_ID:
    raise ValueError("TARGET_CHAT_ID не найден в .env")

def _to_int_or_none(v):
    if v is None or v == "":
        return None
    try:
        return int(v)
    except ValueError:
        return None

TARGET_CHAT_ID = int(TARGET_CHAT_ID)
START_FEED_CHAT_ID = _to_int_or_none(START_FEED_CHAT_ID)
TARGET_CHAT_ID_SLAVIC = _to_int_or_none(TARGET_CHAT_ID_SLAVIC)
TARGET_CHAT_ID_HYBRID = _to_int_or_none(TARGET_CHAT_ID_HYBRID)

def select_target_chat_id(flow_key: str) -> int:
    """
    flow_key: 'slavic' | 'hybrid' | None
    Возвращает чат для отправки заявки по выбранному потоку.
    Если чат для потока не задан — используем TARGET_CHAT_ID.
    """
    if flow_key == "slavic" and TARGET_CHAT_ID_SLAVIC:
        return TARGET_CHAT_ID_SLAVIC
    if flow_key == "hybrid" and TARGET_CHAT_ID_HYBRID:
        return TARGET_CHAT_ID_HYBRID
    return TARGET_CHAT_ID
