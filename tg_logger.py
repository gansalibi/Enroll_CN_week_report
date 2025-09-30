import os
from loguru import logger
from notifiers.logging import NotificationHandler
from env_loader import SECRETS_PATH


token = os.getenv("TG_TOKEN")
chat_id = os.getenv("CHAT_ID_1")

params_chat = {
    "token": token,
    "chat_id": chat_id,
}

tg_handler = NotificationHandler("telegram", defaults=params_chat)
logger.add(tg_handler, level="DEBUG")
