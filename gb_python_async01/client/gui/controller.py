# Обработчик событий (сигналов) между окнами/приложением
import threading
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMessageBox, qApp
from gb_python_async01.client.config import ClientConfig
from gb_python_async01.client.controller import ClientController
from gb_python_async01.client.gui.model import *

from gb_python_async01.utils.observer import ObserverNotifier


class ClientGUIController():
    def __init__(self, config: ClientConfig, app_controller: ClientController,
                 m_contact_selected: ContactSelectedModel, m_contact_list: ContactListModel,
                 m_message_list: MessageListModel,
                 sender_thread: threading.Thread) -> None:
        super().__init__()
        self.config = config
        self.app_controller = app_controller

        self.m_contact_selected = m_contact_selected
        self.m_contact_list = m_contact_list
        self.m_message_list = m_message_list

        self.sender_thread = sender_thread

    def add_contact(self, contact: str) -> bool:
        """ return -> is_ok?"""
        error_txt = self.app_controller.add_contact(contact)
        if error_txt:
            self.show_error_message(f'{error_txt}')
            return False
        else:
            self.m_contact_list.refresh()
            return True

    def delete_contact(self, contact: str):
        error_txt = self.app_controller.del_contact(contact)
        if error_txt:
            self.show_error_message(f'Ошибка при удалении контакта \n {error_txt}')
        else:
            self.m_contact_list.refresh()

    def select_contact(self, contact):
        self.m_contact_selected.set_selected_contact(contact)
        if contact:
            self.m_message_list.refresh(contact)

    def send_message(self, contact: str, msg_txt: str) -> bool:
        """ return -> is_ok?"""
        error_txt = self.app_controller.send_message(receiver=contact, msg_txt=msg_txt)
        if error_txt:
            self.show_error_message(f'Ошибка при отправке сообщения \n {error_txt}')
            return False
        else:
            self.m_message_list.refresh(contact)
            return True

    def check_server_status(self):
        if not self.sender_thread.is_alive():
            self.show_error_message('Server connection broken')
            self.app_quit()

    def app_quit(self):
        qApp.quit()

    def show_error_message(self, error_txt: str):
        msgBox = QMessageBox(QMessageBox.Icon.Critical, "Error", error_txt)
        msgBox.exec_()
