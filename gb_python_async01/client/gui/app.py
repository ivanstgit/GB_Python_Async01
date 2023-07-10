# Графический интерфейс сервера, запускается в отдельном треде
import sys
import threading

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication
from gb_python_async01.client.controller import ClientController

from gb_python_async01.client.db.view import ClientStorage
from gb_python_async01.client.gui.controller import ClientGUIController
from gb_python_async01.client.gui.model import *
from gb_python_async01.client.gui.view import *


class ClientGUI:
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
