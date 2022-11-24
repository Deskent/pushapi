# -*- coding: utf-8 -*-
# pylint: disable=import-error
from __future__ import print_function

from collections import namedtuple

import pushapi.constants as constants
import pushapi.ttypes as pushapi
import pushapi_wrappers as wrappers

HOST_DFL = "10.78.216.60"
PORT_DFL = 9101
NAME_DFL = "Briz_OOO"
TOKEN_DFL = "vvrn3oczp08q1fx34l9y"


class EventDataFromString(wrappers.EventData):
    '''Данные события с содержимым из строки.'''

    def __init__(self, content, attrs=None):
        self.content = content
        super(EventDataFromString, self).__init__(attrs)


class EventDataFromFile(EventDataFromString):
    '''Данные события с подгрузкой из файла.'''

    # В этом примере реализован простейший алгоритм: файл читается целиком.
    # Возможна реализация чтения и отправка файла по чанкам
    def __init__(self, filename, attrs=None):
        with open(filename) as stm:
            content = stm.read().encode()
        super(EventDataFromFile, self).__init__(content, attrs)


class OwnCloud(object):
    '''Класс, отправляющий примеры событий на PushAPI-сервер.
    Attributes:
        event - экземпляр события, которое будет отправлено
        _creds - данные учётной записи (имя компании, токен). Тип: pushapi.Credentials
        _client - клиент PushAPI. Тип: EventProcessor.Client
    '''

    def __init__(
            self,
            event,
            host: str = HOST_DFL,
            port: int = PORT_DFL,
            name: str = NAME_DFL,
            token: str = TOKEN_DFL
    ):
        print(f"Connecting to [{host}:{port}]")
        self._client = wrappers.make_client(host, port)
        print(f"Check credentials: [{name}] : [{token}]")
        self._creds = pushapi.Credentials(name, token)

        self._event = event

    def run(self):
        '''Функция проверяет соединение с сервером и отсылает тестовые события.'''
        # проверка версии и токена
        self._check_server()
        # передача на сервер PushAPI всех тестовых событий
        self._run_demo_event(self._event)

    def _check_server(self):
        '''Проверка версии сервера PushAPI и данных учётной записи.'''

        print(f"Checking server version...")
        client_version = constants.pushapi_version
        server_version = self._client.GetVersion()
        if server_version < client_version:
            raise RuntimeError("incompatible version: client: %d, server: %d" % (client_version, server_version))
        self._client.VerifyCredentials(self._creds)

    def _run_demo_event(self, event):
        '''Формирование и отправка примера события на сервер.
        :param demo_data: данные примера
        '''
        # формируем трифтовую структуру события
        print(f"Make event {event.name}")
        evt = self.make_demo_event(event)
        # отсылаем на сервер
        print(f"Sending event: {event.name}")
        guid = self._send_to_server(evt)
        # сообщаем о выполнении
        print("%s event successfully sent to PushAPI server with guid %s" % (event.name, guid))

    def _send_to_server(self, evt):
        '''Передача на сервер события.
        :param evt: полностью сформированное событие
        :type evt: pushapi.Event
        '''

        print("Begin event")
        event_id = self._client.BeginEvent(evt, self._creds)
        abort_flag = False
        guid = None
        try:
            for data in evt.evt_data:
                print("Begin Stream")
                stream_id = self._client.BeginStream(event_id, data.data_id)
                try:
                    print("Send Stream")
                    self._client.SendStreamData(event_id, stream_id, data.content)
                finally:
                    print("End Stream")
                    self._client.EndStream(event_id, stream_id)
            print("GetEventDatabase")
            guid = self._client.GetEventDatabaseId(event_id)
        except:
            abort_flag = True  # ошибка, завершаем событие с флагом abort
            raise
        finally:
            print("End Event")
            # self._client.EndEvent(event_id, abort_flag)

            print(f"End Event: OK\nGuid: {guid}")
        return guid

    def make_demo_event(self, demo_data):
        '''По описанию примера строит объект Event'''
        evt = wrappers.Event(demo_data.evt_class, demo_data.service)
        self.make_event_attributes(evt, demo_data.name)  # атрибуты события
        evt.add_identities(demo_data.senders, demo_data.receivers)  # добавляем отправителей и получателей
        # добавляем потоки данных, если они заданы
        if demo_data.data_file:
            evt.evt_data = [EventDataFromFile(demo_data.data_file, demo_data.data_attrs)]
        # добавляем сообщения чата, если они заданы
        if demo_data.messages:
            evt.evt_messages = []
            for msg in demo_data.messages:
                assert msg.sender_no < len(evt.evt_senders)  # проверим корректность - такой отправитель есть в списке
                sender_id = evt.evt_senders[msg.sender_no].identity_id  # и получим его идентификатор
                # добавим сообщение к списку
                evt.evt_messages.append(wrappers.ChatMessage(sender_id, msg.sent_time, msg.text))
        return evt

    @staticmethod
    def make_event_attributes(evt, event_name):
        '''Пример заполнения списка атрибутов события.
        :param evt: событие
        :param event_name: имя события
        :type event_name: str
        '''
        # Заполняем обязательные атрибуты
        evt.add_mandatory_attributes()
        # необязательный атрибут - имя события
        if event_name:
            evt.add_attribute("event_name", event_name)
        # можно добавить другие атрибуты - evt.add_attribute("my_attr_name", "my_attr_value")


def create_event():
    # Класс для описания примера
    ExampleDescription = namedtuple(
        "ExampleDescription",
        ["name", "evt_class", "service", "senders", "receivers", "data_file", "data_attrs", "messages"]
    )

    # Классы-надстройки над Identity для создания персон в примерах
    class DemoEmailPerson(wrappers.PersonIdentity):
        '''Идентификация персоны с контактам email.'''

        def __init__(self, email):
            '''Формирует идентификацию персоны с контактами auth и email.
            :param email: адрес электронной почты персоны
            :type email: str
            '''
            # Заполняем контакт email
            contacts = [
                wrappers.EmailContact(email)
            ]
            super(DemoEmailPerson, self).__init__(contacts)

    sender_own_cloud = DemoEmailPerson(email="own_cloud_sender@mail.ru")
    receiver_own_cloud = DemoEmailPerson(email="own_cloud_reveiver@mail.ru")
    own_cloud_data_attrs = [
        # обязательные атрибуты
        pushapi.Attribute(constants.data_attr_file_filename, "own_cloud_test.txt"),
        pushapi.Attribute(constants.data_attr_file_source_file_path, "./own_cloud_test.txt"),
        pushapi.Attribute(constants.data_attr_file_destination_file_path, "own_cloud/temp")
    ]
    event = ExampleDescription(
        name="OwnCloud_test",  # название примера, будет добавлено в атрибуты события
        evt_class=pushapi.EventClass.kFileExchange,  # класс события - kFileExchange
        service="own_cloud_service",  # сервис события -
        senders=[sender_own_cloud],  # отправители
        receivers=[receiver_own_cloud],  # получатель
        data_file="own_cloud_test.txt",  # пересылаемые данные
        data_attrs=own_cloud_data_attrs,  # атрибуты данных - требуется задание имени файла
        messages=None  # сообщения чата - должны быть None для событий класса kFileExchange
    )
    return event


if __name__ == '__main__':
    event = create_event()
    app = OwnCloud(event=event, host=HOST_DFL, port=PORT_DFL, name=NAME_DFL, token=TOKEN_DFL)
    app.run()
