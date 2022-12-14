from flask import Flask, request

from utils import send_message_to_user
from config import settings, logger
from event_creator import (
    EventDescription, NodeCreateEvent, NodeShareEvent, NodeDownloadEvent,
    NodeShareChangePermissionEvent
)
from sender import TrafficMonitor


app = Flask(__name__)

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


def _send_message(data: dict):
    logger.debug("Sending message...")
    text = ''
    try:
        logger.debug(data)
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
            _send_message(request.json)
        return {"result": "OK"}


if __name__ == '__main__':
    app.run(debug=settings.DEBUG, host=settings.APP_HOST, port=settings.APP_PORT)
