# Модели с данными для GUI. Т.к. в проекте исползуется SQLAlchemy, то это скорее интеграционная прослойка

from PyQt5.QtGui import QStandardItemModel, QStandardItem
from gb_python_async01.client.config import ClientConfig

from gb_python_async01.client.db.view import ClientStorage
from gb_python_async01.transport.descriptors import EndpointHost, EndpointPort
from gb_python_async01.utils.observer import Observer, ObserverNotifier


class ContactSelectedModel(ObserverNotifier):
    def __init__(self) -> None:
        super().__init__()
        self.selected_contact = None

    def set_selected_contact(self, contact):
        if contact != self.selected_contact:
            if (not contact) or contact == '':
                self.selected_contact = None
            else:
                self.selected_contact = contact
            self.notifyObservers()


class ContactListModel(ObserverNotifier):
    def __init__(self, db: ClientStorage):
        super().__init__()
        self.db = db
        self.contacts = []
        self.refresh()

    def refresh(self):
        self.contacts = self.db.contact_list()
        self.notifyObservers()


class MessageListModel(ObserverNotifier, Observer):
    def __init__(self, db: ClientStorage, limit=20):
        super().__init__()
        self.db = db
        self.limit = limit
        self.messages = []
        self.contact = None

    def refresh(self, contact: str):
        if contact:
            self.contact = contact
            self.messages = self.db.message_history(contact, limit=self.limit)
        else:
            self.contact = None
            self.messages = []
        self.notifyObservers()

    def modelChanged(self):
        # new incoming message, app controller
        if self.contact:
            self.refresh(self.contact)
