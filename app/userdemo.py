# -*- coding: utf-8 -*-
# pylint: disable=import-error
'''Примеры использования pushAPI.'''

from __future__ import print_function
from collections import namedtuple

# thrift autogenerated modules
import pushapi.ttypes as pushapi
import pushapi.constants as constants

import pushapi_wrappers as wrappers


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
            content = stm.read()
        super(EventDataFromFile, self).__init__(content, attrs)


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


# Классы-надстройки над Identity для создания персон в примерах
class DemoAuthPerson(wrappers.PersonIdentity):
    '''Идентификация персоны с контактами auth и email.'''
    def __init__(self, auth, email):
        '''Формирует идентификацию персоны с контактами auth и email.
        :param auth: имя учетной записи персоны
        :type auth: str
        :param email: адрес электронной почты персоны
        :type email: str
        '''
        # Заполняем контакты: логин, почта, можно добавить скайп и пр.
        contacts = [
            wrappers.AuthContact(auth),
            wrappers.EmailContact(email)
        ]
        super(DemoAuthPerson, self).__init__(contacts)


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


class DemoSkypePerson(wrappers.PersonIdentity):
    '''Идентификация персоны с контактом skype.'''
    def __init__(self, skype_id):
        '''Формирует идентификацию персоны с контактом skype.
        :param skype_id: идентификатор пользователя в скайпе
        :type skype_id: str
        '''
        super(DemoSkypePerson, self).__init__([wrappers.SkypeContact(skype_id)])


class DemoIcqPerson(wrappers.PersonIdentity):
    '''Идентификация персоны с контактом ICQ.'''
    def __init__(self, icq_id):
        '''Формирует идентификацию персоны с контактом ICQ.
        :param icq_id: идентификатор пользователя в ICQ
        :type icq_id: str
        '''
        super(DemoIcqPerson, self).__init__([wrappers.IcqContact(icq_id)])


# Различные идентификации, используемые в примерах
sender_web = DemoAuthPerson("user1@ws1.mycompany.com", "webuser_mail@mycompany.com")
sender_ws_web = wrappers.ComputerIdentity("example_web.mycompany.com")
receiver_web = wrappers.ResourceIdentity("web.example.com", "path/to/target")
sender_ftp = DemoAuthPerson("user2@ws2.company.com", "ftpuser_mail@mycompany.com")
sender_ws_ftp = wrappers.ComputerIdentity("example_ftp.mycompany.com")
receiver_ftp = wrappers.ResourceIdentity("ftp.example.com", "path/to/remote/file.txt")
sender_copy = DemoAuthPerson("user3@ws3.mycompany.com", "flashuser_mail@mycompany.com")
sender_ws_copy = wrappers.ComputerIdentity("example_copyout.mycompany.com")
receiver_copy = wrappers.DeviceIdentity("My flash drive")
sender_print = DemoAuthPerson("user4@ws4.mycompany.com", "printuser_mail@mycompany.com")
receiver_print = wrappers.DeviceIdentity("MyPrinter")
receiver_email1 = DemoEmailPerson("mailuser1@my_company.com")
receiver_email2 = DemoEmailPerson("mailuser2@example.com")
sender_email = DemoEmailPerson("mailuser3@my_company.com")
receiver_webmail1 = DemoEmailPerson("webmailuser4@my_company.com")
receiver_webmail2 = DemoEmailPerson("webmailuser5@example.com")
sender_webmail = DemoEmailPerson("webmailuser6@my_company.com")
receiver_skype1 = DemoSkypePerson("SkypeReceiver1")
receiver_skype2 = DemoSkypePerson("SkypeReceiver2")
sender_skype = DemoSkypePerson("SkypeSender1")
receiver_icq1 = DemoIcqPerson("IcqReceiver1")
receiver_icq2 = DemoIcqPerson("IcqpeReceiver2")
sender_icq = DemoIcqPerson("IcqSender1")


# Класс для описания сообщения чата
ExampleChatMsg = namedtuple(
    "ExampleChatMsg",
    ["text", "sent_time", "sender_no"]
)

# Класс для описания примера
ExampleDescription = namedtuple(
    "ExampleDescription",
    ["name", "evt_class", "service", "senders", "receivers", "data_file", "data_attrs", "messages"]
)

# Описание примера "событие веб"
demo_web = ExampleDescription(
    name="Web example", # название примера, будет добавлено в атрибуты события
    evt_class=pushapi.EventClass.kWeb, # класс события - kWeb
    service=constants.service_web, # сервис события - "web_common"
    senders=[sender_web, sender_ws_web], # отправители - для примера добавлена персона и компьютер
    receivers=[receiver_web], # получатель - веб-ресурс
    data_file="http1.txt", # пересылаемые данные
    data_attrs=None, # атрибуты данных - не требуются
    messages=None # сообщения чата - должны быть None для событий класса kWeb
)

# Атрибуты данных для события пересылки по ftp
ftp_data_attrs = [
    # обязательные атрибуты
    pushapi.Attribute(constants.data_attr_file_filename, "example_filename"),
    pushapi.Attribute(constants.data_attr_file_destination_file_path, "destination/path")
]
# Описание примера события ftp
demo_ftp = ExampleDescription(
    name="FTP example", # название примера, будет добавлено в атрибуты события
    evt_class=pushapi.EventClass.kFileExchange, # класс события - kFileExchange
    service=constants.service_file_ftp, # сервис события - "ftp"
    senders=[sender_ftp, sender_ws_ftp], # отправители - для примера добавлена персона и компьютер
    receivers=[receiver_ftp], # получатель - веб-ресурс
    data_file="ftpfile.txt", # пересылаемые данные
    data_attrs=ftp_data_attrs, # атрибуты данных - требуется задание имени файла
    messages=None # сообщения чата - должны быть None для событий класса kFileExchange
)

# Атрибуты данных для события копирования на съёмное устройство
copy_data_attrs = [
    # обязательные атрибуты
    pushapi.Attribute(constants.data_attr_file_filename, "file.txt"),
    pushapi.Attribute(constants.data_attr_file_source_file_path, "source/file.txt"),
    pushapi.Attribute(constants.data_attr_file_destination_file_path, "destination/path")
]
# Описание примера копирования на съёмное устройство
demo_copy = ExampleDescription(
    name="Copy to removable device example", # название примера, будет добавлено в атрибуты события
    evt_class=pushapi.EventClass.kFileExchange, # класс события - kFileExchange
    service=constants.service_file_removable_storage, # сервис события - "file_copy_removable"
    senders=[sender_copy, sender_ws_copy], # отправители - для примера добавлена персона и компьютер
    receivers=[receiver_copy], # получатель - съёмное устройство
    data_file="copyout_file.txt", # пересылаемые данные
    data_attrs=copy_data_attrs, # атрибуты данных - требуется задание имён файлов (откуда/куда копируется)
    messages=None # сообщения чата - должны быть None для событий класса kFileExchange
)

# Атрибуты данных для события передачи файла по skype
skype_file_data_attrs = [
    # обязательные атрибуты
    pushapi.Attribute(constants.data_attr_file_filename, "file_sent_via_skype.txt"),
]
# Описание примера события обмена файлами в skype
demo_skype_file_exch = ExampleDescription(
    name="Skype file transfer example", # название примера, будет добавлено в атрибуты события
    evt_class=pushapi.EventClass.kFileExchange, # класс события - kFileExchange
    service=constants.service_im_skype, # сервис события - "im_skype"
    senders=[sender_skype], # отправители - для примера добавлен один пользователь skype
    receivers=[receiver_skype1, receiver_skype2], # получатели - для примера добавлены 2 пользователя skype
    data_file="im_file.txt", # пересылаемые данные
    data_attrs=skype_file_data_attrs, # атрибуты данных - требуется задание имени файла
    messages=None # сообщения чата - должны быть None для событий класса kFileExchange
)

# Атрибуты данных для события передачи файла по icq
icq_file_data_attrs = [
    # обязательные атрибуты
    pushapi.Attribute(constants.data_attr_file_filename, "file_sent_via_icq.txt"),
]
# Описание примера события обмена файлами в icq
demo_icq_file_exch = ExampleDescription(
    name="Icq file transfer example", # название примера, будет добавлено в атрибуты события
    evt_class=pushapi.EventClass.kFileExchange, # класс события - kFileExchange
    service=constants.service_im_icq, # сервис события - "im_icq"
    senders=[sender_icq], # отправители - для примера добавлен один пользователь icq
    receivers=[receiver_icq1, receiver_icq2], # получатели - для примера добавлены 2 пользователя icq
    data_file="im_file.txt", # пересылаемые данные
    data_attrs=icq_file_data_attrs, # атрибуты данных - требуется задание имени файла
    messages=None # сообщения чата - должны быть None для событий класса kFileExchange
)

# Сообщения чата
demo_msg1 = ExampleChatMsg(
    text="message 1 text", # текст сообщения
    sent_time="now", # время посылки сообщения
    sender_no=0 # номер отправителя в списке evt_senders
)
demo_msg2 = ExampleChatMsg(
    text="message 2 text", # текст сообщения
    sent_time="2020-03-02T13:45:07+03:00", # время посылки сообщения
    sender_no=0 # номер отправителя в списке evt_senders
)
# Описание примера события обмена сообщениями в skype
demo_skype_msg = ExampleDescription(
    name="Skype dialog example", # название примера, будет добавлено в атрибуты события
    evt_class=pushapi.EventClass.kChat, # класс события - kChat
    service=constants.service_im_skype, # сервис события - "im_skype"
    senders=[sender_skype], # отправители - для примера добавлен один пользователь skype
    receivers=[receiver_skype1, receiver_skype2], # получатели - для примера добавлены 2 пользователя skype
    data_file=None, # данные для события класса kChat передаются в списке messages
    data_attrs=None, # данные для события класса kChat передаются в списке messages
    messages=[demo_msg1, demo_msg2] # сообщения чата
)

# Описание примера события посылки почтового сообщения
demo_mail = ExampleDescription(
    name="Mail example", # название примера, будет добавлено в атрибуты события
    evt_class=pushapi.EventClass.kEmail, # класс события - kEmail
    service=constants.service_email, # сервис события - "email"
    senders=[sender_email], # отправитель - пользователь электронной почты
    receivers=[receiver_email1, receiver_email2], # получатели - пользователи электронной почты
    data_file="test.eml", # данные для события - текст письма с заголовками
    data_attrs=None, # атрибуты данных - не требуются
    messages=None # сообщения чата - должны быть None для событий класса kEmail
)

# Описание примера события посылки сообщения вебпочты
demo_webmail = ExampleDescription(
    name="Webmail example", # название примера, будет добавлено в атрибуты события
    evt_class=pushapi.EventClass.kEmail, # класс события - kEmail
    service=constants.service_email_web, # сервис события - "email_web"
    senders=[sender_webmail], # отправитель - пользователь вебпочты
    receivers=[receiver_webmail1, receiver_webmail2], # получатели - пользователи вебпочты
    data_file="test.eml", # данные для события - текст письма с заголовками
    data_attrs=None, # атрибуты данных - не требуются
    messages=None # сообщения чата - должны быть None для событий класса kEmail
)

# Атрибуты данных для события печати
print_data_attrs = [
    pushapi.Attribute(constants.data_attr_print_job_name, "printer job")
]
# Описание примера события печати
demo_print = ExampleDescription(
    name="Print example", # название примера, будет добавлено в атрибуты события
    evt_class=pushapi.EventClass.kMfp, # класс события - kMfp
    service=constants.service_print, # сервис события - "print"
    senders=[sender_print], # отправитель - персона
    receivers=[receiver_print], # получатель - устройство (принтер)
    data_file="print.txt", # данные, отправленные на печать
    data_attrs=print_data_attrs, # атрибуты данных - требуется задать print_job_name
    messages=None # сообщения чата - должны быть None для событий класса kMfp
)

# Список всех примеров
demo_collection = [
    demo_web, # Веб (class=kWeb service="web_common")
    demo_ftp, # Обмен файлами: FTP (class=kFileExchange service="ftp")
    demo_copy, # Обмен файлами: съёмное устройство (class=kFileExchange service="file_copy_removable")
    demo_skype_file_exch, # Обмен файлами: skype (class=kFileExchange service="im_skype")
    demo_icq_file_exch, # Обмен файлами:  icq (class=kFileExchange service="im_icq")
    demo_skype_msg, # Чат: сообщение skye (class=kChat service="im_skype")
    demo_mail, # Почта: почта на клиенте (class=kEmail service="email")
    demo_webmail, # Почта: почта в браузере (class=kEmail service="email_web")
    demo_print # Печать (class=kMfp service="print")
]

sender_own_cloud = wrappers.DeviceIdentity('OwnCloudSender')
receiver_own_cloud = wrappers.DeviceIdentity("OwnCloudReceiver")
own_cloud_data_attrs = [
    # обязательные атрибуты
    pushapi.Attribute(constants.data_attr_file_filename, "own_cloud_test.txt"),
    pushapi.Attribute(constants.data_attr_file_destination_file_path, "own_cloud/temp")
]
own_cloud = ExampleDescription(
    name="OwnCloud test", # название примера, будет добавлено в атрибуты события
    evt_class=pushapi.EventClass.kFileExchange, # класс события - kFileExchange
    service="own_cloud_service", # сервис события - "ftp"
    senders=[sender_own_cloud], # отправители - для примера добавлена персона и компьютер
    receivers=[receiver_own_cloud], # получатель - веб-ресурс
    data_file="own_cloud_test.txt", # пересылаемые данные
    data_attrs=own_cloud_data_attrs, # атрибуты данных - требуется задание имени файла
    messages=None # сообщения чата - должны быть None для событий класса kFileExchange
)

def make_demo_event(demo_data):
    '''По описанию примера строит объект Event'''
    evt = wrappers.Event(demo_data.evt_class, demo_data.service)
    make_event_attributes(evt, demo_data.name) # атрибуты события
    evt.add_identities(demo_data.senders, demo_data.receivers) # добавляем отправителей и получателей
    # добавляем потоки данных, если они заданы
    if demo_data.data_file:
        evt.evt_data = [EventDataFromFile(demo_data.data_file, demo_data.data_attrs)]
    # добавляем сообщения чата, если они заданы
    if demo_data.messages:
        evt.evt_messages = []
        for msg in demo_data.messages:
            assert msg.sender_no < len(evt.evt_senders) # проверим корректность - такой отправитель есть в списке
            sender_id = evt.evt_senders[msg.sender_no].identity_id # и получим его идентификатор
            # добавим сообщение к списку
            evt.evt_messages.append(wrappers.ChatMessage(sender_id, msg.sent_time, msg.text))
    return evt


class UserDemo(object):
    '''Класс, отправляющий примеры событий на PushAPI-сервер.
    Attributes:
        _creds - данные учётной записи (имя компании, токен). Тип: pushapi.Credentials
        _client - клиент PushAPI. Тип: EventProcessor.Client
    '''

    def __init__(self, host, port, name, token):
        print(f"Connecting to {host}:{port}")
        self._client = wrappers.make_client(host, port)
        self._creds = pushapi.Credentials(name, token)

    def run(self):
        '''Функция проверяет соединение с сервером и отсылает тестовые события.'''
        # проверка версии и токена
        self._check_server()
        # передача на сервер PushAPI всех тестовых событий
        # self._run_demo_event(own_cloud)
        for demo_data in demo_collection:
            self._run_demo_event(demo_data)

    def _check_server(self):
        '''Проверка версии сервера PushAPI и данных учётной записи.'''
        client_version = constants.pushapi_version
        server_version = self._client.GetVersion()
        if server_version < client_version:
            raise RuntimeError("incompatible version: client: %d, server: %d" % (client_version, server_version))
        self._client.VerifyCredentials(self._creds)

    def _run_demo_event(self, demo_data):
        '''Формирование и отправка примера события на сервер.
        :param demo_data: данные примера
        '''
        # формируем трифтовую структуру события
        evt = make_demo_event(demo_data)
        # отсылаем на сервер
        print(f"Sending event: {demo_data.name}")
        guid = self._send_to_server(evt)
        # сообщаем о выполнении
        print("%s event successfully sent to PushAPI server with guid %s" % (demo_data.name, guid))

    def _send_to_server(self, evt):
        '''Передача на сервер события.
        :param evt: полностью сформированное событие
        :type evt: pushapi.Event
        '''
        event_id = self._client.BeginEvent(evt, self._creds)
        abort_flag = False
        try:
            for data in evt.evt_data:
                stream_id = self._client.BeginStream(event_id, data.data_id)
                try:
                    self._client.SendStreamData(event_id, stream_id, data.content)
                finally:
                    self._client.EndStream(event_id, stream_id)
            guid = self._client.GetEventDatabaseId(event_id)
        except:
            abort_flag = True # ошибка, завершаем событие с флагом abort
            raise
        finally:
            self._client.EndEvent(event_id, abort_flag)
        return guid
