from datetime import datetime

import requests
from flask import Flask, request

import pushapi
import pushapi.ttypes
from config import settings, logger
from sender import TrafficMonitor, ExampleChatMsg, ExampleDescription, DemoSkypePerson

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
    message: ExampleChatMsg = create_message_instance(data, text)
    sender = DemoSkypePerson(data.get('owner', "All"))
    receiver = DemoSkypePerson(data.get('receiver', "All"))

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
    sender = TrafficMonitor(
        event=event, host=settings.HOST_DFL, port=settings.PORT_DFL,
        name=settings.NAME_DFL, token=settings.TOKEN_DFL
    )
    sender.send_message()


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
