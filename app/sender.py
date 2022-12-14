# -*- coding: utf-8 -*-
# pylint: disable=import-error
from __future__ import print_function

from collections import namedtuple

import pushapi.constants as constants
import pushapi.ttypes as pushapi
from pushapi import pushapi_wrappers as wrappers
from config import logger


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
            content = stm.read().encode(encoding='utf-8')
        logger.debug(f"Content: {content}")
        super(EventDataFromFile, self).__init__(content, attrs)


class TrafficMonitor(object):
    '''Класс, отправляющий примеры событий на PushAPI-сервер.
    Attributes:
        event - экземпляр события, которое будет отправлено
        _creds - данные учётной записи (имя компании, токен). Тип: pushapi.Credentials
        _client - клиент PushAPI. Тип: EventProcessor.Client
    '''

    def __init__(
            self,
            event,
            host: str,
            port: int,
            name: str,
            token: str
    ):
        logger.debug(f"Connecting to [{host}:{port}]")
        self._client = wrappers.make_client(host, port)
        logger.debug(f"Check credentials: [{name}] : [{token}]")
        self._creds = pushapi.Credentials(name, token)

        self._event = event

    def send_message(self):
        '''Функция проверяет соединение с сервером и отсылает тестовые события.'''
        # проверка версии и токена
        self._check_server()
        # передача на сервер PushAPI всех тестовых событий
        self._run_demo_event(self._event)

    def _check_server(self):
        '''Проверка версии сервера PushAPI и данных учётной записи.'''

        logger.debug(f"Checking server version...")
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
        evt = self.make_demo_event(event)
        # отсылаем на сервер
        guid = self._send_to_server(evt)
        # сообщаем о выполнении
        logger.debug("%s event successfully sent to PushAPI server with guid %s" % (event.name, guid))

    def _send_to_server(self, evt):
        '''Передача на сервер события.
        :param evt: полностью сформированное событие
        :type evt: pushapi.Event
        '''

        event_id = self._client.BeginEvent(evt, self._creds)
        abort_flag = False
        guid = None
        try:
            for data in evt.evt_data:
                stream_id = self._client.BeginStream(event_id, data.data_id)
                try:
                    self._client.SendStreamData(event_id, stream_id, data.content)
                finally:
                    self._client.EndStream(event_id, stream_id)
            guid = self._client.GetEventDatabaseId(event_id)
        except:
            abort_flag = True  # ошибка, завершаем событие с флагом abort
            raise
        finally:
            self._client.EndEvent(event_id, abort_flag)

        return guid

    def make_demo_event(self, data):
        '''По описанию примера строит объект Event'''
        evt = wrappers.Event(data.evt_class, data.service)
        self.make_event_attributes(evt, data.name)  # атрибуты события
        evt.add_identities(data.senders, data.receivers)  # добавляем отправителей и получателей
        # добавляем потоки данных, если они заданы
        if data.data_file:
            evt.evt_data = [EventDataFromFile(data.data_file, data.data_attrs)]
        # добавляем сообщения чата, если они заданы
        if data.messages:
            evt.evt_messages = []
            for msg in data.messages:
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
#
#
# ExampleChatMsg = namedtuple(
#     "ExampleChatMsg",
#     ["text", "sent_time", "sender_no"]
# )
# # Класс для описания примера
# ExampleDescription = namedtuple(
#     "ExampleDescription",
#     ["name", "evt_class", "service", "senders", "receivers", "data_file", "data_attrs", "messages"]
# )

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
#
#
# class DemoSkypePerson(wrappers.PersonIdentity):
#     '''Идентификация персоны с контактом skype.'''
#     def __init__(self, skype_id):
#         '''Формирует идентификацию персоны с контактом skype.
#         :param skype_id: идентификатор пользователя в скайпе
#         :type skype_id: str
#         '''
#         super(DemoSkypePerson, self).__init__([wrappers.SkypeContact(skype_id)])
