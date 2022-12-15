import requests as requests
from flask import Flask, request, Request

from config import settings, logger
from event_creator import (
    EventDescription, NodeCreateEvent, NodeShareEvent, NodeDownloadEvent,
    NodeShareChangePermissionEvent
)
from sender import TrafficMonitor

app = Flask(__name__)


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


def send_message_to_traffic_monitor(event: EventDescription) -> None:
    sender = TrafficMonitor(
        event=event, host=settings.HOST_DFL, port=settings.PORT_DFL,
        name=settings.NAME_DFL, token=settings.TOKEN_DFL
    )
    sender.send_message()


def _get_event(data: dict, text: str = '') -> EventDescription:
    """Return event from request type"""

    request_type: str = data['request_type']

    creators = {
        'node_created': NodeCreateEvent,
        'node_shared': NodeShareEvent,
        'node_downloaded': NodeDownloadEvent,
        'node_share_permission_updated': NodeShareChangePermissionEvent
    }

    creator = creators[request_type]

    return creator(data, text).create_event()


def _send_message(request: Request):
    logger.debug("Sending message...")
    text = ''
    try:
        data = request.json
        file = request.files.get('file')
        logger.debug(f"\n\nFILES: start...")
        for elem in request.files.items():
            logger.debug(f"\n\nFILES: {elem}")

        logger.debug(f"\n\nFILES: FINISH")

        if file:
            data['uploaded_file'] = file
        logger.debug(f'\n{data}')
        send_message_to_user(str(data))
        event: EventDescription = _get_event(data, text)
        send_message_to_traffic_monitor(event)
        text = "Message sent: OK"
        logger.debug(text)
    except KeyError as err:
        text = f"Не смог распознать данные от OwnCloud: {err}"
        logger.error(text)
    except Exception as err:
        text = f"Произошла ошибка при обработке сообщения OwnCloud: {err}"
        logger.error(text)
    send_message_to_user(text)



@app.route('/get_hook', methods=["POST"])
def get_hook():
    if request.method == "POST":
        if request.is_json:
            _send_message(request)
        return {"result": "OK"}


if __name__ == '__main__':
    app.run(debug=settings.DEBUG, host=settings.APP_HOST, port=settings.APP_PORT)
