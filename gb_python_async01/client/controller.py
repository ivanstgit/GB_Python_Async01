# Модуль отвечает за смысловую логику обработки сообщений и взаимодействие компонентов основного приложения
# При этом максимально изолирован от технической реализации остальных компонентов (работает только с абстракциями)
# В части обработки входящих сообщений по сути является самостоятельным приложением (запускается в отдельном потоке)

from datetime import datetime
import threading
import time

from gb_python_async01.client.config import ClientConfig
from gb_python_async01.client.db.view import ClientStorage
from gb_python_async01.client.transport import ClientTransport
from gb_python_async01.transport.errors import EndpointTimeout, JIMValidationError
from gb_python_async01.transport.model.message import *
from gb_python_async01.transport.serializers.user import JIMUserSerializer
from gb_python_async01.utils.errors import UtilsSecurityValidationError
from gb_python_async01.utils.observer import Observer, ObserverNotifier


class ClientController(ObserverNotifier):
    """ App controller - communicates between DB, CLI, Message dispatcher
    Two in one (UI + inbound controller)"""

    def __init__(self, config: ClientConfig, logger,
                 db: ClientStorage, db_lock: threading.Lock,
                 transport: ClientTransport, server_lock: threading.Lock,) -> None:
        super().__init__()
        self.config = config
        self.logger = logger
        self.db = db
        self.db_lock = db_lock
        self.transport = transport
        self.server_lock = server_lock

    def reader_loop(self, timeout=0.1, terminate_on_first_timeout=False):
        while True:
            time.sleep(timeout)
            if not self.server_lock.locked():
                # self.logger.debug(f'{self.user} Reader: try to lock {lock.locked()}')
                with self.server_lock:
                    # self.logger.debug(f'{self.user} Reader: get lock {lock.locked()}')
                    try:
                        action = self.transport.read_action(self.logger)
                    except EndpointTimeout:
                        if terminate_on_first_timeout:
                            break
                    except UtilsSecurityValidationError:
                        # Тут по идее надо и прежние ключи проверять или отдельный тип сообщения
                        # (в базе на сервере зафиксирован ключ из сессии, из которой пришло сообщение)
                        pass
                    else:
                        if action.action == JIMActionMessage.get_action():
                            try:
                                self.process_inbound_message(action)  # type: ignore
                            except Exception as e:
                                self.logger.critical(f'Error ({e}) processing inbound message ({action}) ')
                # self.logger.debug(f'{self.user} Reader: unlocked {lock.locked()}')
            time.sleep(timeout)

    def process_inbound_message(self, action: JIMAction):
        message = self.transport.sec.decrypt_e2e(action.message)  # type: ignore
        with self.db_lock:
            self.db.message_add(contact_name=action.sender,  # type: ignore
                                is_inbound=True,
                                created_at=datetime.fromtimestamp(action.time),
                                msg_txt=message)  # type: ignore
        self.notifyObservers()

    def send_presence(self) -> Optional[str]:
        # Presence (identification) message generation
        action = JIMActionPresence(time=time.time(),
                                   user_account=self.config.user_name,
                                   user_status=f'{self.config.user_name} is here')
        with self.server_lock:
            try:
                response = self.transport.send_action(self.logger, action)
            except Exception as e:
                return 'Ошибка при отправке запроса на сервер'
        if response.is_error:
            return response.error
        return None

    def send_exit(self) -> Optional[str]:
        action = JIMActionExit(time=time.time())
        with self.server_lock:
            try:
                response = self.transport.send_action(self.logger, action)
            except Exception:
                pass
        return None

    def send_message(self, receiver: str, msg_txt: str) -> Optional[str]:
        sender = self.config.user_name
        contact = self.db.contact_get(receiver)
        try:
            if self.transport.sec and contact and contact.pubkey:
                msg_txt_enc = self.transport.sec.encrypt_e2e(msg_txt, contact.pubkey)
            else:
                return 'Ошибка при шифровании сообщения'
        except Exception as e:
            return 'Ошибка при шифровании сообщения'

        action = JIMActionMessage(time=time.time(),
                                  message=msg_txt_enc,
                                  sender=sender,
                                  receiver=receiver)
        with self.server_lock:
            try:
                response = self.transport.send_action(self.logger, action)
            except Exception:
                return 'Ошибка при отправке запроса на сервер'
        if response.is_error:
            return response.error

        with self.db_lock:
            self.db.message_add(contact_name=action.receiver,  # type: ignore
                                is_inbound=False,
                                created_at=datetime.fromtimestamp(action.time),
                                msg_txt=msg_txt)  # type: ignore
        self.notifyObservers()
        return None

    def add_contact(self, contact: str) -> Optional[str]:
        sender = self.config.user_name
        action = JIMActionAddContact(time=time.time(),
                                     user_account=sender,
                                     contact=contact)
        with self.server_lock:
            try:
                response = self.transport.send_action(self.logger, action)
            except Exception:
                return 'Ошибка при отправке запроса на сервер'
        if response.is_error:
            return response.error
        else:
            if response.data:
                try:
                    contacts = list(response.data)
                    with self.db_lock:
                        for contact in contacts:
                            if isinstance(contact, dict):
                                c = JIMUserSerializer.from_dict(contact)
                                self.db.contact_update_from_server(c)
                            else:
                                return 'Ошибка при разборе ответа сервера'
                except JIMValidationError:
                    return 'Ошибка при разборе ответа сервера'
                else:
                    self.notifyObservers()
            else:
                return 'Контакт добавлен, но не готов к приему входящих сообщений. '
        return None

    def del_contact(self, contact: str) -> Optional[str]:
        sender = self.config.user_name
        action = JIMActionDeleteContact(time=time.time(),
                                        user_account=sender,
                                        contact=contact)
        with self.server_lock:
            try:
                response = self.transport.send_action(self.logger, action)
            except Exception:
                return 'Ошибка при отправке запроса на сервер'
        if response.is_error:
            return response.error
        else:
            with self.db_lock:
                self.db.contact_delete(contact_name=contact)
            self.notifyObservers()
        return None

    def synchonize_contacts_from_server(self) -> Optional[str]:
        sender = self.config.user_name
        action = JIMActionGetContacts(time=time.time(),
                                      user_account=sender)
        with self.server_lock:
            try:
                response = self.transport.send_action(self.logger, action)
            except Exception:
                return 'Ошибка при отправке запроса на сервер'
        if response.is_error:
            return response.error
        if response.data:
            contacts = list(response.data)
        else:
            contacts = list()

        with self.db_lock:
            contacts_local = list([c.name for c in self.db.contact_list()])
            contacts_server = list()

            for contact in contacts:
                if isinstance(contact, dict):
                    c = JIMUserSerializer.from_dict(contact)
                    self.db.contact_update_from_server(c)
                    contacts_server.append(c.username)
                else:
                    self.logger.error('Error updating contacts from server')

            for contact in contacts_local:
                if not contact in contacts_server:
                    self.db.contact_delete(contact_name=contact)

        return None
