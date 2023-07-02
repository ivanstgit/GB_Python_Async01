from datetime import datetime
import threading
import time

from gb_python_async01.client.config import ClientConfig
from gb_python_async01.client.db.view import ClientStorage
from gb_python_async01.client.transport import ClientTransport
from gb_python_async01.transport.errors import EndpointTimeout, JIMValidationError
from gb_python_async01.transport.model.message import Action, ActionAddContact, ActionDeleteContact, ActionExit, ActionGetContacts, ActionMessage, ActionPresence
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

    def reader_loop(self, timeout=0.1):
        while True:
            time.sleep(timeout)
            if not self.server_lock.locked():
                # self.logger.debug(f'{self.user} Reader: try to lock {lock.locked()}')
                with self.server_lock:
                    # self.logger.debug(f'{self.user} Reader: get lock {lock.locked()}')
                    try:
                        action = self.transport.read_action()
                    except EndpointTimeout:
                        pass
                    else:
                        if action.action == ActionMessage.get_action():
                            try:
                                self.process_inbound_message(action)  # type: ignore
                            except Exception as e:
                                self.logger.critical(f'Error ({e}) pricessing inbound message ({action}) ')
                # self.logger.debug(f'{self.user} Reader: unlocked {lock.locked()}')
            time.sleep(timeout)

    def process_inbound_message(self, action: Action):
        with self.db_lock:
            self.db.message_add(contact_name=action.sender,  # type: ignore
                                is_inbound=True,
                                created_at=datetime.fromtimestamp(action.time),
                                msg_txt=action.message)  # type: ignore
        self.notifyObservers()

    def send_presence(self):
        # Presence (identification) message generation
        action = ActionPresence(time=time.time(),
                                user_account=self.config.user_name,
                                user_status=f'{self.config.user_name} is here')
        with self.server_lock:
            response = self.transport.send_action(action)
        if response.is_error:
            return response.error
        return None

    def send_exit(self):
        action = ActionExit(time=time.time())
        with self.server_lock:
            response = self.transport.send_action(action)
        if response.is_error:
            return response.error
        return None

    def send_message(self, receiver: str, msg_txt: str):
        sender = self.config.user_name
        action = ActionMessage(time=time.time(),
                               message=msg_txt,
                               sender=sender,
                               receiver=receiver)
        with self.server_lock:
            response = self.transport.send_action(action)
        if response.is_error:
            return response.error

        with self.db_lock:
            self.db.message_add(contact_name=action.receiver,  # type: ignore
                                is_inbound=False,
                                created_at=datetime.fromtimestamp(action.time),
                                msg_txt=action.message)  # type: ignore
        self.notifyObservers()
        return None

    def add_contact(self, contact: str):
        sender = self.config.user_name
        action = ActionAddContact(time=time.time(),
                                  user_account=sender,
                                  contact=contact)
        with self.server_lock:
            response = self.transport.send_action(action)
        if response.is_error:
            return response.error
        else:
            with self.db_lock:
                self.db.contact_add(contact_name=contact)
            self.notifyObservers()
        return None

    def del_contact(self, contact: str):
        sender = self.config.user_name
        action = ActionDeleteContact(time=time.time(),
                                     user_account=sender,
                                     contact=contact)
        with self.server_lock:
            response = self.transport.send_action(action)
        if response.is_error:
            return response.error
        else:
            with self.db_lock:
                self.db.contact_delete(contact_name=contact)
            self.notifyObservers()
        return None

    def synchonize_contacts_from_server(self):
        sender = self.config.user_name
        action = ActionGetContacts(time=time.time(),
                                   user_account=sender)
        with self.server_lock:
            response = self.transport.send_action(action)
        if response.is_error:
            return response.error
        if response.data:
            contacts_server = list(response.data)
        else:
            contacts_server = list()

        with self.db_lock:
            contacts_local = self.db.contact_list()

            for contact in contacts_server:
                if not contact in contacts_local:
                    self.db.contact_add(contact_name=contact)

            for contact in contacts_local:
                if not contact in contacts_server:
                    self.db.contact_delete(contact_name=contact)

        return None
