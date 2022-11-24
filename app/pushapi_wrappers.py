# -*- coding: utf-8 -*-
# pylint: disable=import-error
'''Вспомогательные классы и функции для работы с PushAPI.'''

# common modules
from datetime import datetime
from dateutil.tz import tzlocal # pip install python-dateutil

# apache thrift modules
from thrift.transport import TSSLSocket, TTransport
from thrift.protocol import TBinaryProtocol

# thrift autogenerated modules
from pushapi import EventProcessor
import pushapi.ttypes as pushapi
import pushapi.constants as constants


def make_client(host, port):
    '''Устанавливает соединение с pushAPI-сервером.
    :param host: имя хоста сервера
    :type host: str
    :param port: номер порта
    :type port: int
    :return: экземпляр класса клиента, подключённый к серверу
    :rtype: EventProcessor.Client
    '''
    # Сервер требует подключения по SSL по бинарному протоколу с фреймами
    sock = TSSLSocket.TSSLSocket(host=host, port=port, validate=False)
    transport = TTransport.TFramedTransport(sock)
    transport.open()
    protocol = TBinaryProtocol.TBinaryProtocol(transport)
    return EventProcessor.Client(protocol)


def get_current_datetime_tz():
    '''Возвращает текущее время в формате YYYY-MM-DDThh:mm:ss[+-]hh:mm'''
    return datetime.now(tzlocal()).replace(microsecond=0).isoformat()


def get_next_id():
    '''Возвращает следующий по порядку идентификатор, начиная с 1'''
    get_next_id.counter += 1
    return get_next_id.counter
get_next_id.counter = 0


class Contact(pushapi.ContactWithMeta):
    '''Контакт произвольного типа.'''
    def __init__(self, name, addr, meta=None):
        '''Создаёт новый контакт.
        :param name: тип контакта (auth, email, skype и т.п.)
        :type name: str
        :param addr: контактная информация (логин, email-адрес и т.п.)
        :type addr: str
        :param meta: дополнительная информация о контакте
        :type meta: str
        '''
        super(Contact, self).__init__(pushapi.Attribute(name, addr), meta)


class AuthContact(Contact):
    '''Контакт авторизованного пользователя.'''
    def __init__(self, addr, meta=None):
        super(AuthContact, self).__init__(constants.contact_type_auth, addr, meta)


class EmailContact(Contact):
    '''Контакт электронной почты.'''
    def __init__(self, addr, meta=None):
        super(EmailContact, self).__init__(constants.contact_type_email, addr, meta)


class SkypeContact(Contact):
    '''Контакт skype.'''
    def __init__(self, addr, meta=None):
        super(SkypeContact, self).__init__(constants.contact_type_skype, addr, meta)


class IcqContact(Contact):
    '''Контакт ICQ.'''
    def __init__(self, addr, meta=None):
        super(IcqContact, self).__init__(constants.contact_type_icq, addr, meta)


class HostnameContact(Contact):
    '''Контакт доменное имя.'''
    def __init__(self, addr, meta=None):
        super(HostnameContact, self).__init__(constants.contact_type_dnshostname, addr, meta)


class Identity(pushapi.Identity):
    '''Идентификация произвольного типа.'''
    def __init__(self, id_type, contacts=None, attrs=None):
        '''Создаёт нвую идентификацию.
        :param id_type: тип идентификации (персона, компьютер, устройство, веб-ресурс)
        :type id_type: pushapi.IdentityItemType
        :param contacts: контакты идентификации
        :type contacts: list (items type: pushapi.ContactWithMeta)
        :param attrs: аттрибуты идентификации
        :type attrs: list (items type: pushapi.Attribute)
        '''
        if attrs is None:
            attrs = [] # список атрибутов должен быть задан, хотя бы пустой
        # Инициализация трифтовой структуры
        # identity_id = Identity._counter - обязательный параметр - уникальный номер идентификации
        # identity_type = id_type - обязательный параметр - тип идентификации
        # identity_contacts = [] - обязательный параметр - устаревшее поле, оставено для совместимости
        # identity_attributes = attrs - обязательый параметр - список атрибутов (может быть пустым)
        # identity_contacts_with_meta = contacts - опциональный параметр - список контактов
        super(Identity, self).__init__(get_next_id(), id_type, [], attrs, contacts)

    def add_contact(self, contact_type, value, meta=None):
        '''Добавление нового контакта.
        :param contact_type: тип контакта
        :type contact_type: str
        :param value: контактная информация
        :type value: str
        :param meta: дополнительная информация
        :type meta: str
        '''
        # identity_contacts_with_meta определён в _init__() базового класса
        # pylint: disable=access-member-before-definition
        if self.identity_contacts_with_meta is None:
            self.identity_contacts_with_meta = []
        self.identity_contacts_with_meta.append(Contact(contact_type, value, meta))


class PersonIdentity(Identity):
    '''Идентификация персоны.'''
    def __init__(self, contacts=None):
        # NB: у персоны не может быть атрибутов
        super(PersonIdentity, self).__init__(pushapi.IdentityItemType.kPerson, contacts)


class WorkstationIdentity(Identity):
    '''Идентификация рабочей станции.'''
    def __init__(self, contacts=None, attrs=None):
        super(WorkstationIdentity, self).__init__(pushapi.IdentityItemType.kWorkstation, contacts, attrs)


class ComputerIdentity(WorkstationIdentity):
    '''Идентификация компьютера.'''
    def __init__(self, name=None, contacts=None, attrs=None):
        '''Формирует идентификацию типа 'компьютер'
        :param name: имя компьютера
        :type name: str
        :param contacts: см. Identity.__init__()
        :type contacts: list
        :param attrs: см. Identity.__init__()
        :type attrs: list
        '''
        # формируем контакт hostname, если задано имя компьютера
        name_contact = HostnameContact(name) if name else None
        # и добавляем его к списку контактов
        contacts = _add_item(contacts, name_contact)
        # формируем атрибут типа рабочей станции (=компьютер)
        computer_attr = pushapi.Attribute(constants.identity_attr_ws_type, constants.ws_type_computer)
        # и добавляем его к списку атрибутов
        attrs = _add_item(attrs, computer_attr)
        # инициализируем базовый класс
        super(ComputerIdentity, self).__init__(contacts, attrs)


class DeviceIdentity(Identity):
    '''Идентификация устройства.'''
    def __init__(self, name, contacts=None, attrs=None):
        '''Формирует идентификацию типа 'устройство'.
        :param name: имя устройства
        :type name: str
        :param contacts: см. Identity.__init__()
        :type contacts: list
        :param attrs: см. Identity.__init__()
        :type attrs: list
        '''
        # обязательный атрибут: identity_attr_device_name
        assert name
        name_attr = pushapi.Attribute(constants.identity_attr_device_name, name)
        # могут быть заданы опциональные атрибуты: identity_attr_device_type ...
        attrs = _add_item(attrs, name_attr)
        # инициализируем базовый класс
        super(DeviceIdentity, self).__init__(pushapi.IdentityItemType.kDevice, contacts, attrs)


class ResourceIdentity(Identity):
    '''Идентификация веб-ресурса.'''
    def __init__(self, domain_name, path, contacts=None, attrs=None):
        '''Формирует идентификацию типа 'ресурс'.
        :param domain_name: доменное имя ресурса
        :type domain_name: str
        :param path: путь ресурса
        :type path: str
        :param contacts: см. Identity.__init__()
        :type contacts: list
        :param attrs: см. Identity.__init__()
        :type attrs: list
        '''
        # обязательные атрибуты: identity_attr_resource_address dentity_attr_resource_url
        identity_attrs = [
            pushapi.Attribute(constants.identity_attr_resource_address, domain_name),
            pushapi.Attribute(constants.identity_attr_resource_url, path)
        ]
        # опциональные атрибуты
        if attrs:
            identity_attrs.extend(attrs)
        # инициализируем базовый класс
        super(ResourceIdentity, self).__init__(pushapi.IdentityItemType.kResource, contacts, identity_attrs)


class EventData(pushapi.EventData):
    '''Данные события'''
    def __init__(self, attrs=None):
        super(EventData, self).__init__(get_next_id(), attrs)


class ChatMessage(pushapi.ChatMessage):
    '''Сообщение чата - обёртка над трифтовой структурой.'''
    def __init__(self, sender_id, sent_time, text, data_id=None):
        '''Инициализация трифтовой структуры ChatMessage.
        :param sender_id: отправитель (=identity_id одного из элементов evt_senders события) (обязательный параметр)
        :type sender_id: int
        :param sent_time: время передачи сообщения (YYYY-MM-DDThh:mm:ss[+-]hh:mm либо "now" - текущее) (обязательный параметр)
        :type sent_time: str
        :param text: текст сообщения в кодировке utf8 (обязательный параметр)
        :type text: str
        :param data_id: идентификатор потока данных. Если задан data_id, текст сообщения находится в указанном
                        потоке, text должен быть равен пустой строке. Служит для передачи очень больших сообщений,
                        когда передача через строку становится неэффективной. Используется редко. (опциональный параметр)
        :type data_id: int
        '''
        # обработаем специальное значение даты
        if sent_time == "now":
            sent_time = get_current_datetime_tz()
        # инициализируем трифтовый класс
        super(ChatMessage, self).__init__(sender_id, sent_time, text, data_id)


class ItemLink(pushapi.ItemLink):
    '''Описание связи между различными элементами события.'''
    def __init__(self, from_id, to_id, name):
        '''Инициализация трифтовой структуры ItemLink.
        :param from_id: идентификатор элемента, от которого идёт связь (required в pushapi.thrift)
        :type from_id: int
        :param to_id: идентификатор элемента, к которому идёт связь (required в pushapi.thrift)
        :type to_id: int
        :param name: имя (тип) связи
        :type name: str
        '''
        # инициализируем трифтовый класс
        super(ItemLink, self).__init__(from_id, to_id, name)


class Event(pushapi.Event):
    '''Событие.'''
    def __init__(self, evt_class, service, attribs=None, senders=None, receivers=None, data=None,
                 messages=None, links=None, source=None, destination=None):
        '''Формирует событие pushapi.
        :param evt_class: класс события (required в pushapi.thrift)
        :type evt_class: pushapi.EventClass
        :param service: сервис события (required в pushapi.thrift)
        :type service: str
        :param attribs: список атрибутов события (optional в pushapi.thrift)
        :type attribs: list (items type pushapi.Attribute)
        :param senders: список отправителей (required в pushapi.thrift)
        :type senders: list (items type Identity)
        :param receives: список получателей (required в pushapi.thrift)
        :type receivers: list (items type Identity)
        :param data: данные для передачи (required в pushapi.thrift)
        :type data: EventData
        :param messages: список сообщений чата (required в pushapi.thrift)
        :type messages: list (items type ChatMessage)
        :param links: связи между элементами события. Используется редко (optional в pushapi.thrift)
        :type links: list (items type ItemLink)
        :param source: источник события (optional в pushapi.thrift)
        ^type source: Identity
        :param destination: приёмник события (optional в pushapi.thrift)
        :type destination: Identity
        '''
        # обязательные поля не могут быть None, но допускаются пустые списки
        if senders is None:
            senders = []
        if receivers is None:
            receivers = []
        if data is None:
            data = []
        # инициализируем трифтовый класс
        super(Event, self).__init__(evt_class, service, attribs, senders, receivers, data, messages, links, source, destination)

    def add_attribute(self, name, value):
        '''Добавление атрибута к списку атрибутов события.
        :param name: имя атрибута
        :type name: str
        :param value: значение атрибута
        :type value: str
        '''
        if self.evt_attributes is None:
            self.evt_attributes = []
        self.evt_attributes.append(pushapi.Attribute(name, value))

    def add_mandatory_attributes(self, capture_date=None, capture_server_ip="127.0.0.1", capture_server_fqdn="my_capture_server.example.com"):
        '''Добавление обязательных атрибутов события.
        :param capture_date: время перехвата в формате YYYY-MM-DDThh:mm:ss[+-]hh:mm
        :type capture_date: str
        :param capture_server_ip: ip-адрес сервера перехвата
        :type capture_server_ip: str
        :param capture_server_fqdn: полное доменное имя сервера перехвата
        :type capture_server_fqdn: str
        '''
        # Устанавливаем время перехвата, если оно не задано
        if not capture_date:
            capture_date = get_current_datetime_tz()

        # обязательные атрибуты
        evt_attribs = [
            # время перехвата с таймзоной
            pushapi.Attribute(constants.event_attr_capture_date, capture_date),
            # IP сервера, на котором произошёл перехват
            pushapi.Attribute(constants.event_attr_capture_server_ip, capture_server_ip),
            # имя сервера, на котором произошёл перехват
            pushapi.Attribute(constants.event_attr_capture_server_fqdn, capture_server_fqdn)
        ]
        if self.evt_attributes is None:
            self.evt_attributes = []
        self.evt_attributes.extend(evt_attribs)

    def add_senders(self, identity_list):
        '''Добавление отправителей.
        :param identity_list: список отправителей
        :type identity_list: list (items type pushapi.Identity)
        '''
        self.evt_senders.extend(identity_list)

    def add_receivers(self, identity_list):
        '''Добавление получателей.
        :param identity_list: список получателей
        :type identity_list: list (items type pushapi.Identity)
        '''
        self.evt_receivers.extend(identity_list)

    def add_identities(self, senders, receivers):
        '''Добавление отправителей/получателей.
        :param senders: список отправителей
        :type senders: list (items type pushapi.Identity)
        :param receivers: список получателей
        :type receivers: list (items type pushapi.Identity)
        '''
        if senders:
            self.add_senders(senders)
        if receivers:
            self.add_receivers(receivers)


def _add_item(vect, item):
    if item is not None:
        vect = [] if vect is None else vect[:]
        vect.append(item)
    return vect