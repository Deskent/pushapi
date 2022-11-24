import os
import datetime
from collections import namedtuple

from flask import Flask, request

import pushapi as constants
import pushapi as pushapi
from pushapi_class import OwnCloud

HOST_DFL = os.getenv("HOST_DFL")
PORT_DFL = int(os.getenv("PORT_DFL"))
NAME_DFL = os.getenv("NAME_DFL")
TOKEN_DFL = os.getenv("TOKEN_DFL")

app = Flask(__name__)


def get_message(data: dict) -> str:
    file_name: str = data['name']
    owner: str = data['owner']
    date_time: datetime.datetime = datetime.datetime.fromtimestamp(data['datetime'])
    return (
        f"Отправитель: {owner}\n"
        f"Имя файла: {file_name}\n"
        f"Время публикации: {date_time}"
    )


def send_message_to_traffic_monitor(message: str) -> None:
    ExampleChatMsg = namedtuple(
        "ExampleChatMsg",
        ["text", "sent_time", "sender_no"]
    )
    ExampleDescription = namedtuple(
        "ExampleDescription",
        ["name", "evt_class", "service", "senders", "receivers", "data_file", "data_attrs", "messages"]
    )
    demo_msg1 = ExampleChatMsg(
        text=message,  # текст сообщения
        sent_time="now",  # время посылки сообщения
        sender_no=0  # номер отправителя в списке evt_senders
    )
    msg = ExampleDescription(
        name="Skype dialog example",  # название примера, будет добавлено в атрибуты события
        evt_class=pushapi.EventClass.kChat,  # класс события - kChat
        service=constants.service_im_skype,  # сервис события - "im_skype"
        senders=[sender_skype],  # отправители - для примера добавлен один пользователь skype
        receivers=[receiver_skype1, receiver_skype2],  # получатели - для примера добавлены 2 пользователя skype
        data_file=None,  # данные для события класса kChat передаются в списке messages
        data_attrs=None,  # данные для события класса kChat передаются в списке messages
        messages=[demo_msg1]  # сообщения чата
    )
    pushapi_sender = OwnCloud(
        event=msg,
        host=HOST_DFL,
        port=PORT_DFL,
        name=NAME_DFL,
        token=TOKEN_DFL
    )
    pushapi_sender.run()
    print(message)


@app.route('/get_hook', methods=["POST"])
def get_hook():
    if request.method == "POST":
        if request.is_json:
            try:
                message: str = get_message(request.json)
            except KeyError as err:
                message: str = f"Не смог распознать данные от OwnCloud: {err}"
            except Exception as err:
                message: str = f"Произошла ошибка при обработке сообщения OwnCloud: {err}"
            send_message_to_traffic_monitor(message)
        else:
            print("Data:", request.data)
        return {"result": "OK"}


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=8989, load_dotenv=True)
