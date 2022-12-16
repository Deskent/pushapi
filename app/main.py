import requests as requests
from flask import Flask, request, Request

from config import settings, logger
from event_creator import (
    EventDescription, NodeCreateEvent, NodeShareEvent, NodeDownloadEvent,
    NodeShareChangePermissionEvent, EventCreator, FileTransmittingEvent
)
from sender import TrafficMonitor

app = Flask(__name__)


def send_message_to_user(message: str) -> None:
    """Send message to telegram"""

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
    """Send event to Traffic Monitor using settings from .env file"""
    logger.debug(f"\nSend event to Traffic Monitor...")
    sender = TrafficMonitor(
        event=event, host=settings.HOST_DFL, port=settings.PORT_DFL,
        name=settings.NAME_DFL, token=settings.TOKEN_DFL
    )
    try:
        sender.send_message()
    except Exception as err:
        logger.error(err)
    logger.debug(f"\nSend event to Traffic Monitor: OK")


def _get_event_creator(data: dict) -> EventCreator:
    """Return event from request type"""

    request_type: str = data['request_type']

    creators = {
        'node_created': NodeCreateEvent,
        'node_shared': NodeShareEvent,
        'node_downloaded': NodeDownloadEvent,
        'node_share_permission_updated': NodeShareChangePermissionEvent
    }

    return creators[request_type]


def _get_event(data: dict, text: str = '') -> EventDescription:
    """Return event data"""

    creator: EventCreator = _get_event_creator(data)

    logger.debug(f'\n{data}')
    send_message_to_user(str(data))

    return creator(data, text).create_event()


def _send_message(request: Request) -> None:
    """Create event and send it to Traffic monitor"""

    logger.debug("Sending message...")
    text = ''
    try:
        data = request.json

        if request.is_json:
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
    """Get POST request and send it to Traffic Monitor"""

    # _send_message(request)
    return {"result": "get_hook: OK"}


@app.route('/get_file', methods=["POST"])
def get_file():
    """Get POST request and send it to Traffic Monitor"""

    data = dict(request.form)
    file = request.files.get('file')
    report = (
        f"\nFile: {file}" 
        f"\nFile name: {file.name}" 
        f"\nFile.filename: {file.filename}"
        f"\nData: {data}"
    )
    logger.debug(report)
    send_message_to_user(report)
    text = f"File sent: {file}"
    # extensions = ('.doc', '.docx', '.xls', '.xlsx', '.pdf')'
    # TODO заменить
    extensions = ('.doc', '.docx', '.xls', '.xlsx', '.pdf', '.txt')

    if file and file.filename.endswith(extensions):
        logger.debug("\nTry to create event...")
        data['uploaded_file'] = file
        file_event: EventDescription = FileTransmittingEvent(data).create_event()
        logger.info(f"\n\nFILE_EVENT: {file_event}")
        send_message_to_traffic_monitor(file_event)
        text = "File sent: OK"
    send_message_to_user(text)

    return {"result": "get_file: OK"}


if __name__ == '__main__':
    app.run(debug=settings.DEBUG, host=settings.APP_HOST, port=settings.APP_PORT)
