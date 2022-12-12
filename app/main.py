import sys
from datetime import datetime
from pathlib import Path

import requests
from flask import Flask, request
import logging.config

import pushapi
import pushapi.ttypes
from config import settings
from sender import OwnCloud, ExampleChatMsg, ExampleDescription, DemoSkypePerson

app = Flask(__name__)

logs_dir_name = 'logs'
logs_dir_full_path = Path().cwd() / logs_dir_name
log_level = "DEBUG" if settings.DEBUG else "WARNING"

logger_conf = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {
        "base": {
            "format": '[%(asctime)s] %(levelname)s [%(filename)s:%(name)s.%(funcName)s:%(lineno)d]: %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": log_level,
            "formatter": "base",
            "stream": sys.stdout
        },
        "errors": {
            "class": 'logging.FileHandler',
            "level": 'ERROR',
            "formatter": "base",
            "filename": f"{logs_dir_name}/errors.log",
            "mode": "a"
        }
    },
    "loggers": {
        "pushapi": {
            "level": log_level,
            "handlers": ['console', 'errors'],
            "filters": [],
            "propagate": 1,
        }
    }
}

logging.config.dictConfig(logger_conf)
logger = logging.getLogger('pushapi')


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


def create_message_instance(data: dict, text: str = '') -> ExampleChatMsg:
    logger.debug("Getting message instance...")

    if not text:
        text: str = get_message(data)
        logger.debug(f"Got message text: {text}")
    return ExampleChatMsg(
        text=text,  # текст сообщения
        sent_time="now",  # время посылки сообщения
        sender_no=0  # номер отправителя в списке evt_senders
    )


def get_message_event(data: dict, text: str = '') -> ExampleDescription:
    logger.debug("Getting message event...")
    message: ExampleChatMsg = create_message_instance(data, text)
    logger.debug(f"Got message instance: {message}")
    sender = DemoSkypePerson(data.get('owner', "All"))
    logger.debug(f"Sender: {sender}")
    receiver = DemoSkypePerson(data.get('receiver', "All"))
    logger.debug(f"Receiver: {receiver}")

    message_event = ExampleDescription(
        name="OwnCloud_test_message_name2",  # название примера, будет добавлено в атрибуты события
        evt_class=pushapi.ttypes.EventClass.kChat,  # класс события - kChat
        service="im_skype",
        senders=[sender],  # отправители - для примера добавлен один пользователь skype
        receivers=[receiver],  # получатели - для примера добавлены 2 пользователя skype
        data_file=None,  # данные для события класса kChat передаются в списке messages
        data_attrs=None,  # данные для события класса kChat передаются в списке messages
        messages=[message]  # сообщения чата
    )
    logger.debug(f"Getting message event: OK\n{message_event}")

    return message_event


def send_message_to_traffic_monitor(event: ExampleDescription) -> None:
    sender = OwnCloud(
        event=event, host=settings.HOST_DFL, port=settings.PORT_DFL,
        name=settings.NAME_DFL, token=settings.TOKEN_DFL
    )
    sender.run()


def get_message(data: dict) -> str:
    if not data:
        return "Message data parse error"
    file_name: str = data.get('name', "Filename error")
    owner: str = data.get('owner', "Owner error")
    date_time: datetime = datetime.fromtimestamp(data.get('datetime'))
    return (
        f"Владелец: {owner}\n"
        f"Имя файла: {file_name}\n"
        f"Размер файла (bytes): {data.get('size')}\n"
        f"Время публикации: {date_time}"
    )


@app.route('/get_hook', methods=["POST"])
def get_hook():
    """
    {
        'name': 'help.txt',
        'size': 788,
        'path': '/Bitrix1/files/help.txt',
        'internalPath': 'files/help.txt',
        'id': 21394,
        'owner': 'Bitrix1',
        'datetime': 1666779532
    }
    :return:
    """
    if request.method == "POST":
        if request.is_json:
            logger.debug("Sending message...")
            data = {}
            text = ''
            try:
                data: dict = request.json
                logger.debug(data)
                # TODO удалить в проде:
                send_message_to_user(message=str(data))
                # *****
                message_event: ExampleDescription = get_message_event(data, text)
                send_message_to_traffic_monitor(message_event)
                logger.debug("Message sent: OK")
            except KeyError as err:
                text = f"Не смог распознать данные от OwnCloud: {err}"
                logger.error(text)
            except Exception as err:
                text = f"Произошла ошибка при обработке сообщения OwnCloud: {err}"
                logger.error(text)

        return {"result": "OK"}


if __name__ == '__main__':
    app.run(debug=settings.DEBUG, host=settings.APP_HOST, port=settings.APP_PORT)
