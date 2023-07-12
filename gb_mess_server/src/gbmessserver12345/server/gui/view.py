""" Графические компоненты интерфейса. Простейшие обработчики определены сразу, межкомпонентные - в контроллере"""
from typing_extensions import override

from PyQt5.QtCore import QItemSelection, Qt, pyqtSlot
from PyQt5.QtGui import QIntValidator
from PyQt5.QtWidgets import (
    QAbstractItemView,
    QAction,
    QDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from gbmessserver12345.server.gui.controller import ServerGUIController
from gbmessserver12345.server.gui.model import (
    ActiveUsersModel,
    SettingsModel,
    SingleSelectionModel,
    UserModel,
    UserStatisticsModel,
)
from gbmessserver12345.common.transport.descriptors import EndpointPort
from gbmessserver12345.common.utils.observer import Observer


class MainWindow(QMainWindow, Observer):
    def __init__(self, model: ActiveUsersModel, controller: ServerGUIController):
        super().__init__()
        self.model = model
        self.controller = controller

        self.model.refresh()
        self.initUI()
        self.model_changed(None)

    def initUI(self):
        # Кнопка выхода
        exitAction = QAction("Выход", self)
        exitAction.setShortcut("Ctrl+Q")
        exitAction.triggered.connect(self.controller.app_quit)

        # Кнопка обновить список клиентов
        self.refresh_button = QAction("Обновить список", self)
        self.refresh_button.triggered.connect(self.controller.notify_observers)

        # Кнопка настроек сервера
        self.config_btn = QAction("Настройки сервера", self)
        self.config_btn.triggered.connect(self.controller.show_settings_window)

        # Кнопка вывести историю сообщений
        self.show_history_button = QAction("История клиентов", self)
        self.show_history_button.triggered.connect(self.controller.show_stat_window)

        # Кнопка вывести диалог ведения пользователей
        self.show_user_button = QAction("Учетные записи", self)
        self.show_user_button.triggered.connect(self.controller.show_user_window)

        # Статусбар
        # dock widget
        self.statusBar()

        # Тулбар
        self.toolbar = self.addToolBar("MainBar")
        self.toolbar.addAction(exitAction)
        self.toolbar.addAction(self.refresh_button)
        self.toolbar.addAction(self.show_history_button)
        self.toolbar.addAction(self.config_btn)
        self.toolbar.addAction(self.show_user_button)

        # Настройки геометрии основного окна
        # Поскольку работать с динамическими размерами мы не умеем, и мало времени на изучение, размер окна фиксирован.
        self.setFixedSize(800, 600)
        self.setWindowTitle("Messaging Server alpha release")

        # Надпись о том, что ниже список подключённых клиентов
        self.label = QLabel("Список подключённых клиентов:", self)
        self.label.setFixedSize(240, 15)
        self.label.move(10, 25)

        # Окно со списком подключённых клиентов.
        self.active_clients_table = QTableView(self)
        self.active_clients_table.move(10, 45)
        self.active_clients_table.setFixedSize(780, 400)
        self.active_clients_table.setModel(self.model)

        # Последним параметром отображаем окно.
        self.show()

    @override
    def model_changed(self, notifier):
        self.statusBar().showMessage("Server Working")
        self.model.refresh()
        self.active_clients_table.resizeColumnsToContents()
        self.active_clients_table.resizeRowsToContents()


# Класс окна с историей пользователей
class StatisticsWindow(QDialog, Observer):
    def __init__(self, model: UserStatisticsModel, controller: ServerGUIController):
        super().__init__()

        self.model = model
        self.controller = controller

        self.initUI()
        self.model_changed(None)

    def initUI(self):
        # Настройки окна:
        self.setWindowTitle("Статистика клиентов")
        self.setFixedSize(600, 700)
        # self.setAttribute(Qt. WA_DeleteOnClose)

        # Кнапка закрытия окна
        self.close_button = QPushButton("Закрыть", self)
        self.close_button.move(250, 650)
        self.close_button.clicked.connect(self.controller.hide_stat_window)

        # Лист с собственно историей
        self.history_table = QTableView(self)
        self.history_table.move(10, 10)
        self.history_table.setFixedSize(580, 620)
        self.history_table.setModel(self.model)

    @override
    def model_changed(self, notifier):
        self.model.refresh()
        self.history_table.resizeColumnsToContents()
        self.history_table.resizeRowsToContents()


# # Класс окна настроек


class SettingsWindow(QDialog, Observer):
    def __init__(self, model: SettingsModel, controller: ServerGUIController):
        self.model = model
        self.controller = controller
        super().__init__()
        self.initUI()
        self.model_changed(None)

    def initUI(self):
        # Настройки окна
        self.setFixedSize(500, 160)
        self.setWindowTitle("Настройки сервера")

        # Надпись о файле базы данных:
        self.db_url_label = QLabel("Строка подключения к базе данных: ", self)
        self.db_url_label.move(10, 10)
        self.db_url_label.setFixedSize(480, 15)

        # Строка с путём базы (current)
        self.db_url_display = QLineEdit(self)
        self.db_url_display.setFixedSize(480, 20)
        self.db_url_display.move(10, 30)
        self.db_url_display.setEnabled(False)

        # Строка с путём базы
        self.db_url_edit = QLineEdit(self)
        self.db_url_edit.setFixedSize(480, 20)
        self.db_url_edit.move(10, 55)
        self.db_url_edit.textEdited.connect(self.change_db_url)

        # Метка с номером порта
        self.port_display_label = QLabel("Порт для соединений (текущий):", self)
        self.port_display_label.move(10, 85)
        self.port_display_label.setFixedSize(300, 20)

        # Поле для номера порта
        self.port_display = QLineEdit(self)
        self.port_display.move(310, 85)
        self.port_display.setFixedSize(200, 20)
        self.port_display.setEnabled(False)

        self.port_display_label = QLabel("Порт для соединений (новый):", self)
        self.port_display_label.move(10, 105)
        self.port_display_label.setFixedSize(300, 20)

        self.port_validator = QIntValidator(
            EndpointPort.min_value, EndpointPort.max_value, self
        )
        # Поле для ввода номера порта
        self.port_edit = QLineEdit(self)
        self.port_edit.move(310, 105)
        self.port_edit.setFixedSize(200, 20)
        self.port_edit.setValidator(self.port_validator)
        self.port_edit.textEdited.connect(self.change_port)

        # Кнопка сохранения настроек
        self.save_btn = QPushButton("Сохранить", self)
        self.save_btn.move(190, 130)
        self.save_btn.clicked.connect(self.controller.save_server_config)

        # Кнапка закрытия окна
        self.close_button = QPushButton("Закрыть", self)
        self.close_button.move(275, 130)
        self.close_button.clicked.connect(self.controller.hide_settings_window)

    def change_db_url(self):
        self.model.db_url = self.db_url_edit.text()

    def change_port(self):
        self.model.port = self.port_edit.text()

    @override
    def model_changed(self, notifier):
        self.db_url_display.setText(self.model.db_url)
        if self.db_url_edit.text() == "":
            self.db_url_edit.setText(self.model.db_url)
        self.port_display.setText(str(self.model.port))
        if self.port_edit.text() == "":
            self.port_edit.setText(str(self.model.port))


class UserWindow(QDialog, Observer):
    """Класс диалог регистрации пользователя на сервере."""

    def __init__(
        self,
        m_table: UserModel,
        m_selected: SingleSelectionModel,
        controller: ServerGUIController,
    ):
        super().__init__(flags=Qt.WindowType.Window)

        self.m_table = m_table
        self.m_selected = m_selected
        self.controller = controller

        self.setWindowTitle("Регистрация")
        self.setBaseSize(600, 500)
        self.init_ui()

    def init_ui(self):
        self.list_table = QTableView()
        self.list_table.setModel(self.m_table)
        self.list_table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.list_table.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )
        # self.list_table.clicked.connect
        self.list_table.selectionModel().selectionChanged.connect(self.user_selection_changed)  # type: ignore
        # self.list_table.setSelectionModel(self.m_selected)
        # currentItemChanged.connect(self.current_item_changed)  # type: ignore

        self.gr_add = QGroupBox("Добавление пользователя")
        self.gr_add_layout = QVBoxLayout()

        self.label_username = QLabel("Имя пользователя:")
        self.gr_add_layout.addWidget(self.label_username)
        self.client_name = QLineEdit()
        self.client_name.setMaxLength(30)
        self.gr_add_layout.addWidget(self.client_name)

        self.label_passwd = QLabel("Пароль:")
        self.gr_add_layout.addWidget(self.label_passwd)
        self.client_passwd = QLineEdit()
        self.client_passwd.setEchoMode(QLineEdit.Password)
        self.gr_add_layout.addWidget(self.client_passwd)

        self.label_conf = QLabel("Подтверждение пароля:")
        self.gr_add_layout.addWidget(self.label_conf)

        self.client_conf = QLineEdit(self)
        self.client_conf.setEchoMode(QLineEdit.Password)
        self.gr_add_layout.addWidget(self.client_conf)

        self.gr_add_layout2 = QHBoxLayout()

        self.btn_add = QPushButton("Добавить \n пользователя")
        self.btn_add.clicked.connect(self.add_user)
        self.gr_add_layout2.addWidget(self.btn_add)

        self.btn_pass = QPushButton("Изменить \n пароль")
        self.btn_pass.clicked.connect(self.set_password)
        self.gr_add_layout2.addWidget(self.btn_pass)
        self.gr_add_layout.addLayout(self.gr_add_layout2)

        self.spacer = QWidget()
        self.spacer.setBaseSize(20, 1000)
        self.gr_add_layout.addWidget(self.spacer, 100, Qt.AlignmentFlag.AlignLeft)

        self.gr_add.setLayout(self.gr_add_layout)

        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)

        main_layout.addWidget(self.list_table, 50, Qt.AlignmentFlag.AlignLeft)
        main_layout.addWidget(self.gr_add, 1, Qt.AlignmentFlag.AlignLeft)
        self.setLayout(main_layout)

        self.messages = QMessageBox()

    @pyqtSlot(QItemSelection, QItemSelection)
    def user_selection_changed(
        self, selected: QItemSelection, deselected: QItemSelection
    ):
        """Подставить в форму данные выбранного пользователя"""
        rows = self.list_table.selectionModel().selectedRows()
        for row in rows:
            row_index = row.row()
            value = self.m_table.get_user_in_row(row_index)
            self.m_selected.set_selected(value)
            self.client_name.setText(value)

    def add_user(self):
        """
        Метод проверки правильности ввода и сохранения в базу нового пользователя.
        """
        user_name = self.client_name.text()
        password = self.client_passwd.text()
        if not user_name:
            self.messages.critical(self, "Ошибка", "Не указано имя пользователя.")
            return
        if password != self.client_conf.text():
            self.messages.critical(self, "Ошибка", "Введённые пароли не совпадают.")
            return

        error = self.m_table.add_user(user_name, password)
        if error:
            self.messages.critical(self, "Ошибка", error)
            return
        self.client_passwd.clear()
        self.client_conf.clear()

    def set_password(self):
        """
        Метод проверки правильности ввода и сохранения в базу нового пароля.
        """
        user_name = self.client_name.text()
        password = self.client_passwd.text()
        if not user_name:
            self.messages.critical(self, "Ошибка", "Не указано имя пользователя.")
            return
        if password != self.client_conf.text():
            self.messages.critical(self, "Ошибка", "Введённые пароли не совпадают.")
            return

        error = self.m_table.set_password(user_name, password)
        if error:
            self.messages.critical(self, "Ошибка", error)
            return
        self.client_passwd.clear()
        self.client_conf.clear()
