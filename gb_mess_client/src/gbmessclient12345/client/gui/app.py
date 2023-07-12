# Графический интерфейс сервера, запускается в отдельном треде
import sys
import threading

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication

from gbmessclient12345.client.config import ClientConfig
from gbmessclient12345.client.controller import ClientController
from gbmessclient12345.client.db.view import ClientStorage
from gbmessclient12345.client.gui.controller import ClientGUIController
from gbmessclient12345.client.gui.model import (
    ContactListModel,
    ContactSelectedModel,
    MessageListModel,
)
from gbmessclient12345.client.gui.view import MainWindow


class ClientGUI:
    """Основное GUI-приложение"""

    def __init__(
        self, config: ClientConfig, db: ClientStorage, app_controller: ClientController
    ) -> None:
        self.db = db
        self.config = config
        self.app_controller = app_controller

    def run(self, sender_thread: threading.Thread):
        client_app = QApplication(sys.argv)

        m_contact_selected = ContactSelectedModel()
        m_contact_list = ContactListModel(self.db)
        m_message_list = MessageListModel(self.db)

        # inconimg messages
        self.app_controller.add_observer(m_message_list)

        controller = ClientGUIController(
            self.config,
            self.app_controller,
            m_contact_selected,
            m_contact_list,
            m_message_list,
            sender_thread,
        )

        view = MainWindow(
            self.config, controller, m_contact_selected, m_contact_list, m_message_list
        )

        timer = QTimer()
        timer.timeout.connect(controller.check_server_status)
        timer.start(1000)

        client_app.exec_()
        timer.stop()
