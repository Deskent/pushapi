import datetime

import requests
from flask import Flask, request

import pushapi
import pushapi.ttypes
from config import settings
from sender import OwnCloud, ExampleChatMsg, ExampleDescription, DemoSkypePerson

app = Flask(__name__)


def send_message_to_user(message: str) -> None:
    """
    The function of sending the message with the result of the script
    """
    telegram_id = settings.TELEGRAM_ID
    if not telegram_id or not settings.TELEBOT_TOKEN:
        print("Can`t send report to telegram: no token or ID")
        return
    url: str = (
        f"https://api.telegram.org/bot{settings.TELEBOT_TOKEN}/sendMessage?"
        f"chat_id={telegram_id}"
        f"&text={message}"
    )
    try:
        requests.get(url, timeout=5)
        print(f"telegram id: {telegram_id}\n message: {message}")
    except Exception as err:
        print(f"telegram id: {telegram_id}\n message: {message}\n requests error: {err}")


def get_message(data: dict) -> str:
    if not data:
        return "Message data parse error"
    file_name: str = data.get('name', "Filename error")
    owner: str = data.get('owner', "Owner error")
    date_time: datetime.datetime = datetime.datetime.fromtimestamp(data['datetime'])
    return (
        f"Отправитель: {owner}\n"
        f"Имя файла: {file_name}\n"
        f"Время публикации: {date_time}"
    )


def create_message_instance(data: dict, text: str = '') -> ExampleChatMsg:
    print("Getting message instance...")

    if not text:
        text: str = get_message(data)
        print(f"Got message text: {text}")
    return ExampleChatMsg(
        text=text,  # текст сообщения
        sent_time="now",  # время посылки сообщения
        sender_no=0  # номер отправителя в списке evt_senders
    )


def get_message_event(data: dict, text: str = '') -> ExampleDescription:
    print("Getting message event...")
    message: ExampleChatMsg = create_message_instance(data, text)
    print(f"Got message instance: {message}")
    sender = DemoSkypePerson(data.get('owner', "All"))
    print(f"Sender: {sender}")
    receiver = DemoSkypePerson(data.get('receiver', "All"))
    print(f"Receiver: {receiver}")

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
    print(f"Getting message event: OK\n{message_event}")

    return message_event


def get_default_event(text: str):
    sender = DemoSkypePerson("OwnCloud error")
    receiver = DemoSkypePerson("All")
    message = ExampleChatMsg(
        text=text,  # текст сообщения
        sent_time="now",  # время посылки сообщения
        sender_no=0  # номер отправителя в списке evt_senders
    )
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

    return message_event


def send_message_to_traffic_monitor(event: ExampleDescription) -> None:
    sender = OwnCloud(
        event=event, host=settings.HOST_DFL, port=settings.PORT_DFL,
        name=settings.NAME_DFL, token=settings.TOKEN_DFL
    )
    sender.run()


@app.route('/get_hook', methods=["POST"])
def get_hook():
    if request.method == "POST":
        if request.is_json:
            data = {}
            text = ''
            try:
                data: dict = request.json
                print(data)
                send_message_to_user(message=str(data))
            except KeyError as err:
                text = f"Не смог распознать данные от OwnCloud: {err}"
                print(text)
            except Exception as err:
                text = f"Произошла ошибка при обработке сообщения OwnCloud: {err}"
                print(text)

            message_event: ExampleDescription = get_message_event(data, text)
            print(message_event)
            # send_message_to_traffic_monitor(message_event)
        else:
            print("Data:", request.data)
        return {"result": "OK"}


if __name__ == '__main__':
    app.run(debug=settings.DEBUG, host=settings.APP_HOST, port=settings.APP_PORT)
