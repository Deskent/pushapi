import requests as requests

from config import settings, logger


def send_message_to_user(message: str) -> None:
    """
    The function of sending the message with the result of the script
    """
    telegram_id = settings.TELEGRAM_ID
    if not telegram_id or not settings.TELEBOT_TOKEN:
        logger.debug("Can`t send report to telegram: no token or ID")
        return
    url: str = (
        f"https://api.telegram.org/bot{settings.TELEBOT_TOKEN}/sendMessage?"
        f"chat_id={telegram_id}"
        f"&text={message}"
    )
    try:
        requests.get(url, timeout=5)
        logger.debug(f"telegram id: {telegram_id}\n message: {message}")
    except Exception as err:
        logger.debug(f"telegram id: {telegram_id}\n message: {message}\n requests error: {err}")
