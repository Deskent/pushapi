from flask import Flask, request, Request

from config import settings, logger
from event_creator import (
    EventDescription, NodeCreateEvent, NodeShareEvent, NodeDownloadEvent,
    NodeShareChangePermissionEvent, EventCreator
)
from sender import TrafficMonitor

app = Flask(__name__)


def send_message_to_traffic_monitor(event: EventDescription) -> None:
    """Send event to Traffic Monitor using settings from .env file"""

    logger.debug(f"Send event to Traffic Monitor...")
    sender = TrafficMonitor(
        event=event, host=settings.HOST_DFL, port=settings.PORT_DFL,
        name=settings.NAME_DFL, token=settings.TOKEN_DFL
    )
    try:
        sender.send_message()
    except Exception as err:
        logger.error(err)
    logger.debug(f"Send event to Traffic Monitor: OK")


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

    return creator(data, text).create_event()


def _send_message(request: Request) -> None:
    """Create event and send it to Traffic monitor"""

    logger.debug("Sending message...")
    text = ''
    try:
        data = request.json
        logger.debug(f'\n\n{data}\n')
        if request.is_json:
            event: EventDescription = _get_event(data, text)
            send_message_to_traffic_monitor(event)
    except KeyError as err:
        text = f"Не смог распознать данные от OwnCloud: {err}"
        logger.exception(text)
    except Exception as err:
        text = f"Произошла ошибка при обработке сообщения OwnCloud: {err}"
        logger.exception(text)


@app.route('/get_hook', methods=["POST"])
def get_hook():
    """Get POST request and send it to Traffic Monitor"""

    _send_message(request)
    return {"result": "get_hook: OK"}


if __name__ == '__main__':
    app.run(debug=settings.DEBUG, host=settings.APP_HOST, port=settings.APP_PORT)
