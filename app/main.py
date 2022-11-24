import os
import datetime

from flask import Flask, request
import pushapi
import pushapi.ttypes
from sender import OwnCloud, ExampleChatMsg, ExampleDescription, DemoSkypePerson

HOST_DFL = os.getenv("HOST_DFL")
PORT_DFL = int(os.getenv("PORT_DFL"))
NAME_DFL = os.getenv("NAME_DFL")
TOKEN_DFL = os.getenv("TOKEN_DFL")

app = Flask(__name__)


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
        event=event, host=HOST_DFL, port=PORT_DFL, name=NAME_DFL, token=TOKEN_DFL
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
            except KeyError as err:
                text = f"Не смог распознать данные от OwnCloud: {err}"
                print(text)
            except Exception as err:
                text = f"Произошла ошибка при обработке сообщения OwnCloud: {err}"
                print(text)

            message_event: ExampleDescription = get_message_event(data, text)
            send_message_to_traffic_monitor(message_event)
        else:
            print("Data:", request.data)
        return {"result": "OK"}


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=8989, load_dotenv=True)
