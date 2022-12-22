from abc import abstractmethod
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

import pushapi.ttypes
from config import logger
from pushapi import pushapi_wrappers as wrappers


@dataclass
class ChatMessage:
    text: str
    sent_time: str = 'now'
    sender_no: int = 0


@dataclass
class EventDescription:
    name: str
    evt_class: object
    senders: list
    receivers: list
    service: str = 'im_skype'
    data_file: Optional[str] = None
    data_attrs: Optional[list] = None
    messages: Optional[list] = None


class SkypePerson(wrappers.PersonIdentity):
    """Идентификация персоны с контактом skype."""

    def __init__(self, skype_id):
        """Формирует идентификацию персоны с контактом skype.

        :param skype_id: идентификатор пользователя в скайпе
        :type skype_id: str
        """

        super(SkypePerson, self).__init__([wrappers.SkypeContact(skype_id)])


class EventCreator:
    """Abstract Base class for creating events using data from OwnCloud"""

    def __init__(self, data: dict, text: str = ''):
        self.data: dict = data
        self.text: str = text
        self.sender: Optional[SkypePerson] = None
        self.receiver: Optional[SkypePerson] = None
        self.request_type: str = 'OwnCloud: unrecognized request type'
        self.event_type: pushapi.ttypes.EventClass = pushapi.ttypes.EventClass.kChat
        self.file_name: str = Path(self.data['path']).name
        self.owner: str = self.data['owner']
        self.message: str = (
            f'Владелец: {self.owner}\n'
            f'Имя файла: {self.file_name}\n'
        )

    @abstractmethod
    def create_event(self):
        pass

    def _get_sender(self):
        self.sender = SkypePerson(self.owner)
        if not self.sender:
            self.sender = 'All'
        return self.sender

    def _get_receiver(self):
        receiver: str = self.data.get('share_with', 'All')
        if not receiver:
            receiver = "All"
        self.receiver = SkypePerson(receiver)
        return self.receiver


class EventCreatorWithMessage(EventCreator):
    """Abstract class for creating message event using data from OwnCloud"""

    def create_event(self):
        message: ChatMessage = self._create_message_instance()
        sender: SkypePerson = self._get_sender()
        receiver: SkypePerson = self._get_receiver()

        return EventDescription(
            name=self.request_type,
            evt_class=self.event_type,
            senders=[sender],
            receivers=[receiver],
            messages=[message],
            service='im_skype',
            data_file=None,
            data_attrs=[],
        )

    def _create_message_instance(self):
        if not self.text:
            if not self.data:
                self.text = 'Message data parse error'
            else:
                self.text: str = self._get_message()
            logger.debug(f'Got message text: {self.text}')
        return ChatMessage(
            text=self.text,
            sent_time='now',
            sender_no=0
        )

    @staticmethod
    def _get_from_timestamp(stamp: int) -> datetime:
        return datetime.fromtimestamp(stamp)

    @abstractmethod
    def _get_message(self) -> str:
        pass


class NodeCreateEvent(EventCreatorWithMessage):
    """"Realise send message about OwnCloud uploaded file"""

    def __init__(self, data: dict, text: str = ''):
        super().__init__(data, text)
        self.request_type = 'OwnCloud: загружен файл'
        self.message = f'\n{self.request_type}:\n' + self.message

    def _get_message(self):
        date_time: datetime = self._get_from_timestamp(self.data.get('datetime'))
        self.message += (
            f'Размер файла (bytes): {self.data.get("size")}\n'
            f'Дата создания файла: {date_time}'
        )

        return self.message


class NodeDownloadEvent(EventCreatorWithMessage):
    """"Realise send message about OwnCloud downloaded file"""

    def __init__(self, data: dict, text: str = ''):
        super().__init__(data, text)
        self.request_type = 'OwnCloud: файл скачан'
        self.message = f'\n{self.request_type}:\n' + self.message

    def _get_message(self) -> str:
        downloaded_by: str = self.data.get('downloaded_by', 'Downloader error')
        self.message += (
            f'Скачал: {downloaded_by}\n'
            f'Размер файла (bytes): {self.data.get("size")}\n'
        )
        timestamp = self.data.get("timestamp")
        if timestamp:
            self.message += f'\nВремя: {self._get_from_timestamp(timestamp)}'

        return self.message


class NodeShareEvent(EventCreatorWithMessage):
    """"Realise send message about OwnCloud file permission opened"""

    def __init__(self, data: dict, text: str = ''):
        super().__init__(data, text)
        self.request_type = 'OwnCloud: открыт доступ к файлу'
        self.message = f'\n{self.request_type}:\n' + self.message

    def _get_share_type(self):
        share_type: str = str(self.data.get('share_type'))

        share_types = {
            '0': f'\nДля пользователя: {self.data.get("share_with")}',
            '1': f'\nДля группы: {self.data.get("share_with")}',
            '3': f'\nПо ссылке',
            '4': f'\nГостям: {self.data.get("share_with")}',
        }
        return share_types.get(share_type, 'Share type not defined')

    def _get_message(self) -> str:
        expiration = self.data.get("expiration")
        if expiration:
            self.message += f'\nИстекает: {self._get_from_timestamp(expiration)}'

        self.message += self._get_share_type()
        if self.data.get('passwordEnabled'):
            self.message += '\nТребуется пароль.'
        logger.debug(self.message)

        return self.message


class NodeShareChangePermissionEvent(NodeShareEvent):
    """"Realise send message about OwnCloud file permission changed"""

    def __init__(self, data: dict, text: str = ''):
        super().__init__(data, text)
        self.request_type = 'OwnCloud: права на доступ к файлу изменены'
        self.message = f'\n{self.request_type}:\n' + self.message


class FileTransmittingEvent(EventCreator):
    """"Realise send file from OwnCloud event"""

    def __init__(self, data: dict, text: str = ''):
        super().__init__(data, text)
        self.request_type = f'OwnCloud: передача файла: {self.file_name}'
        self.message = f'\n{self.request_type}:\n' + self.message
        self.event_type = pushapi.ttypes.EventClass.kFileExchange

    def create_event(self):
        sender: SkypePerson = self._get_sender()
        receiver: SkypePerson = self._get_receiver()
        file_name = self.data['uploaded_file']
        file_data_attrs = [
            pushapi.ttypes.Attribute(name="filename", value=file_name),
        ]

        return EventDescription(
            name=self.request_type,
            evt_class=self.event_type,
            senders=[sender],
            receivers=[receiver],
            messages=[],  # должен быть пустым при отправке файла
            service='im_skype',
            data_file=file_name,
            data_attrs=file_data_attrs,
        )
