import os
from loguru import logger
from notifiers.logging import NotificationHandler
from dotenv import load_dotenv
load_dotenv()

token = os.getenv("TG_TOKEN")
chat_id = os.getenv("CHAT_ID")

params_chat = {
    "token": token,
    "chat_id": chat_id,
}

tg_handler = NotificationHandler("telegram", defaults=params_chat)
logger.add(tg_handler, level="DEBUG")
