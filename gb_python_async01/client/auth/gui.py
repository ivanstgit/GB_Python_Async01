from typing import Optional
from PyQt5.QtCore import Qt, QItemSelection, pyqtSlot
from PyQt5.QtGui import QIntValidator, QWindow
from PyQt5.QtWidgets import (QAction, QDialog, QAbstractItemView, QGroupBox,
                             QLabel, QLineEdit, QMainWindow, QMessageBox, QHBoxLayout, QVBoxLayout, QWidget,
                             QPushButton, QTableView, QTableWidget)

from gb_python_async01.client.transport import ClientTransport


class LoginWindow(QDialog):
    '''Класс диалог регистрации пользователя на сервере.'''

    def __init__(self, logger, controller: ClientTransport, user_name: Optional[str], password: Optional[str]):
        super().__init__(flags=Qt.WindowType.Window)

        self.logger = logger
        self.controller = controller

        self.setWindowTitle('Регистрация')
        self.setBaseSize(600, 500)
        self.init_ui()

        if user_name:
            self.client_name.setText(user_name)
        if password:
            self.client_passwd.setText(password)

        if user_name and password:
            self.connect()

    def init_ui(self):

        self.main_layout = QVBoxLayout()

        self.label_username = QLabel('Имя пользователя:')
        self.main_layout.addWidget(self.label_username)
        self.client_name = QLineEdit()
        self.client_name.setMaxLength(30)
        self.main_layout.addWidget(self.client_name)

        self.label_passwd = QLabel('Пароль:')
        self.main_layout.addWidget(self.label_passwd)
        self.client_passwd = QLineEdit()
        self.client_passwd.setEchoMode(QLineEdit.Password)
        self.main_layout.addWidget(self.client_passwd)

        self.btn_connect = QPushButton('Подключиться')
        self.btn_connect.clicked.connect(self.connect)
        self.main_layout.addWidget(self.btn_connect)

        self.setLayout(self.main_layout)

        self.messages = QMessageBox()
        self.setStatusTip('')

    def connect(self):
        '''
        Метод проверки правильности ввода и сохранения в базу нового пользователя.
        '''
        user_name = self.client_name.text()
        password = self.client_passwd.text()
        if not user_name:
            self.messages.critical(
                self, 'Ошибка', 'Не указано имя пользователя.')
            return
        if password == '':
            self.messages.critical(
                self, 'Ошибка', 'Не указан пароль.')
            return

        self.setStatusTip('Подключение к серверу')
        error = self.controller.connect(self.logger)
        if error:
            self.messages.critical(
                self, 'Ошибка', error)
            return
        self.client_passwd.clear()

        self.setStatusTip('Проверка логина и пароля')
        error = self.controller.login(self.logger, user_name, password)
        if error:
            self.messages.critical(
                self, 'Ошибка', error)
            return

        self.close()
