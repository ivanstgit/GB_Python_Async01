""" Графические компоненты интерфейса. Простейшие обработчики определены сразу, межкомпонентные - в контроллере """

from typing_extensions import override
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QIntValidator
from PyQt5.QtWidgets import (
    QAction,
    QAbstractItemView,
    QDialog,
    QFileDialog,
    QGridLayout,
    QGroupBox,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTableView,
    QWidget,
    QScrollArea,
    QHBoxLayout,
    QVBoxLayout,
    QFrame,
    QSizePolicy,
)

from gb_python_async01.client.config import ClientConfig
from gb_python_async01.client.gui.controller import ClientGUIController
from gb_python_async01.client.gui.model import (
    ContactListModel,
    MessageListModel,
    ContactSelectedModel,
)
from gb_python_async01.utils.observer import Observer


class MainWindow(QMainWindow):
    """Главное окно приложения"""

    def __init__(
        self,
        config: ClientConfig,
        controller: ClientGUIController,
        m_contact_selected: ContactSelectedModel,
        m_contact_list: ContactListModel,
        m_message_list: MessageListModel,
    ):
        super().__init__()
        self.config = config
        self.controller = controller
        self.m_contact_selected = m_contact_selected
        self.m_contact_list = m_contact_list
        self.m_message_list = m_message_list

        self.initUI()

    def initUI(self):
        self.setWindowTitle(f"Messaging Client alpha release ({self.config.user_name})")
        # self.setFixedSize(800, 600)
        self.setContentsMargins(0, 0, 0, 0)

        main = QFrame(self)
        main.setBaseSize(200, 600)

        # Кнопка выхода
        exitAction = QAction("Выход", self)
        exitAction.setShortcut("Ctrl+Q")
        exitAction.triggered.connect(self.controller.app_quit)

        # left panel - contacts
        self.gr_contacts = ContactsGroupBox(
            "Contact list",
            self.controller,
            self.m_contact_selected,
            self.m_contact_list,
        )
        self.gr_messages = MessagesGroupBox(
            "Message list",
            self.controller,
            self.m_contact_selected,
            self.m_message_list,
        )

        # main.setFixedSize(700, 500)
        main.setContentsMargins(0, 0, 0, 0)

        main_layout = QGridLayout()

        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.gr_contacts, 0, 0)
        main_layout.addWidget(self.gr_messages, 0, 1)
        main_layout.setColumnMinimumWidth(0, 40)
        main_layout.setColumnMinimumWidth(0, 120)
        main_layout.setColumnStretch(0, 40)
        main_layout.setColumnStretch(1, 60)

        main.setLayout(main_layout)

        self.setCentralWidget(main)

        self.statusBar().showMessage(
            f"Connected to server {self.config.srv_host}:{self.config.srv_port}"
        )
        self.show()


class ContactsGroupBox(QGroupBox, Observer):
    """Компонент со списком контактов и функциями добавления/удаления"""

    def __init__(
        self,
        title: str,
        controller: ClientGUIController,
        m_contact_selected: ContactSelectedModel,
        m_contact_list: ContactListModel,
    ):
        super().__init__(title=title, parent=None)

        self.m_contact_selected = m_contact_selected
        self.m_contact_list = m_contact_list
        self.controller = controller

        self.initUI()
        self.model_changed(None)

        self.m_contact_selected.add_observer(self)
        self.m_contact_list.add_observer(self)

    def initUI(self):
        self.list_table = QListWidget()
        self.list_table.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )
        self.list_table.currentItemChanged.connect(self.current_item_changed)  # type: ignore

        self.add_label = QLabel()
        self.add_label.setText("Add contact")

        self.add_edit = QLineEdit()
        self.add_edit.setMaxLength(30)
        self.add_edit.setEnabled(True)
        self.add_edit.setBaseSize(300, 20)
        self.add_edit.setMinimumWidth(170)
        self.add_edit.returnPressed.connect(self.add_contact)

        self.add_button = QPushButton("Add")
        self.add_button.setEnabled(True)
        self.add_button.clicked.connect(self.add_contact)

        self.del_button = QPushButton("Delete selected contact")
        self.del_button.setEnabled(False)
        self.del_button.clicked.connect(self.del_contact)

        main_layout = QGridLayout()
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)

        main_layout.addWidget(self.list_table, 0, 0, Qt.AlignmentFlag.AlignLeft)
        main_layout.setRowStretch(0, 75)

        main_layout.addWidget(self.add_label, 1, 0, Qt.AlignmentFlag.AlignLeft)
        main_layout.setRowMinimumHeight(1, 20)
        main_layout.setRowStretch(1, 1)
        main_add_layout = QHBoxLayout()
        main_add_layout.setContentsMargins(0, 0, 0, 0)
        main_add_layout.addWidget(self.add_edit, 90, Qt.AlignmentFlag.AlignLeft)
        main_add_layout.addWidget(self.add_button, 10, Qt.AlignmentFlag.AlignLeft)
        main_layout.addLayout(main_add_layout, 2, 0, Qt.AlignmentFlag.AlignLeft)
        main_layout.setRowMinimumHeight(2, 20)
        main_layout.setRowStretch(2, 1)
        main_layout.addWidget(self.del_button, 3, 0, Qt.AlignmentFlag.AlignLeft)

        main_layout.setRowMinimumHeight(2, 20)
        main_layout.setRowStretch(3, 1)
        # main_layout.setColumnStretch(0, 4)

        self.setLayout(main_layout)
        self.del_button.adjustSize()

    @override
    def model_changed(self, notifier):
        """Обработчик изменения модели"""
        if notifier == None or notifier == self.m_contact_list:
            self.list_table.clear()
            for contact in self.m_contact_list.contacts:
                item = QListWidgetItem(contact)
                self.list_table.addItem(item)

        if notifier == None or notifier == self.m_contact_selected:
            if self.m_contact_selected.selected_contact:
                self.del_button.setEnabled(True)
            else:
                self.del_button.setEnabled(False)

    def add_contact(self):
        is_ok = self.controller.add_contact(self.add_edit.text())
        if is_ok:
            self.add_edit.clear()

    def del_contact(self):
        contact = self.m_contact_selected.selected_contact
        if contact:
            self.controller.delete_contact(contact)

    @pyqtSlot(QListWidgetItem, QListWidgetItem)
    def current_item_changed(self, current: QListWidgetItem, previous: QListWidgetItem):
        if current:
            self.controller.select_contact(current.text())
        else:
            self.controller.select_contact(None)


class MessagesGroupBox(QGroupBox, Observer):
    def __init__(
        self,
        title: str,
        controller: ClientGUIController,
        m_contact_selected: ContactSelectedModel,
        m_message_list: MessageListModel,
    ):
        super().__init__(title=title, parent=None)
        self.controller = controller
        self.m_contact_selected = m_contact_selected
        self.m_message_list = m_message_list

        self.initUI()
        self.model_changed(None)
        self.m_contact_selected.add_observer(self)
        self.m_message_list.add_observer(self)
        self.list_table.scrollToBottom()

    def initUI(self):
        """Инициализировать интерфейс"""
        self.contact_label = QLabel()

        self.list_table = QListWidget()
        self.list_table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.list_table.setMinimumWidth(400)
        self.list_table.setAutoScroll(True)
        self.list_table.setWordWrap(True)

        self.add_label = QLabel()
        self.add_label.setText("Enter message")

        self.add_edit = QLineEdit()
        self.add_edit.setMaxLength(250)
        self.add_edit.setBaseSize(600, 20)
        self.add_edit.setMinimumWidth(290)
        self.add_edit.setMaximumWidth(800)
        self.add_edit.setEnabled(True)
        self.add_edit.returnPressed.connect(self.send_message)

        self.add_button = QPushButton("Send message")
        self.add_button.setEnabled(True)
        self.add_button.clicked.connect(self.send_message)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)

        main_layout.addWidget(self.contact_label, 1, Qt.AlignmentFlag.AlignLeft)

        main_layout.addWidget(self.list_table, 100, Qt.AlignmentFlag.AlignLeft)
        self.list_table.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )

        main_layout.addWidget(self.add_label, 1, Qt.AlignmentFlag.AlignLeft)

        main_add_layout = QHBoxLayout()
        main_add_layout.setContentsMargins(0, 0, 0, 0)
        main_add_layout.addWidget(self.add_edit, 75, Qt.AlignmentFlag.AlignLeft)
        self.add_edit.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        main_add_layout.addWidget(self.add_button, 1, Qt.AlignmentFlag.AlignLeft)
        self.add_button.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        main_layout.addLayout(main_add_layout, 0)

        self.setLayout(main_layout)

    @override
    def model_changed(self, notifier):
        """Обработать выбор контакта"""
        if not notifier or notifier == self.m_contact_selected:
            contact = self.m_contact_selected.selected_contact
            if contact:
                self.contact_label.setText(f"Conversation with {contact}")
                self.list_table.setEnabled(True)
                self.add_edit.setEnabled(True)
                self.add_button.setEnabled(True)
            else:
                self.contact_label.setText("Select contact for conversation")
                self.list_table.setEnabled(False)
                self.add_edit.setEnabled(False)
                self.add_edit.clear()
                self.add_button.setEnabled(False)

        if not notifier or notifier == self.m_message_list:
            self.list_table.clear()
            for message in self.m_message_list.messages:
                item = QListWidgetItem(str(message), None)
                self.list_table.addItem(item)
            self.list_table.scrollToBottom()

    def send_message(self):
        """Отправить текстовое сообщение пользователю"""
        contact = self.m_contact_selected.selected_contact
        msg_txt = self.add_edit.text()
        if msg_txt != "" and contact:
            is_ok = self.controller.send_message(contact, msg_txt)
            if is_ok:
                self.add_edit.clear()
