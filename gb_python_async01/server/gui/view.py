
# Графические компоненты интерфейса. Простейшие обработчики определены сразу, межкомпонентные - в контроллере
# Принципиально не реализована бредовая логика по изменению хоста и выбору пути к файлу БД
# Изменения порта и строки подключения для демонстрации работы приложения вполне достаточно, кмк
from PyQt5.QtGui import QIntValidator
from PyQt5.QtWidgets import (QAction, QDialog, QFileDialog,
                             QLabel, QLineEdit, QMainWindow, QMessageBox,
                             QPushButton, QTableView)

from gb_python_async01.server.gui.controller import ServerGUIController
from gb_python_async01.server.gui.model import *
from gb_python_async01.utils.observer import Observer


class MainWindow(QMainWindow, Observer):
    def __init__(self, model: ActiveUsersModel, controller: ServerGUIController):
        super().__init__()
        self.model = model
        self.controller = controller

        self.model.refresh()
        self.initUI()
        self.modelChanged()

    def initUI(self):
        # Кнопка выхода
        exitAction = QAction('Выход', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.triggered.connect(self.controller.app_quit)

        # Кнопка обновить список клиентов
        self.refresh_button = QAction('Обновить список', self)
        self.refresh_button.triggered.connect(self.controller.notifyObservers)

        # Кнопка настроек сервера
        self.config_btn = QAction('Настройки сервера', self)
        self.config_btn.triggered.connect(self.controller.show_settings_window)

        # Кнопка вывести историю сообщений
        self.show_history_button = QAction('История клиентов', self)
        self.show_history_button.triggered.connect(self.controller.show_stat_window)

        # Статусбар
        # dock widget
        self.statusBar()

        # Тулбар
        self.toolbar = self.addToolBar('MainBar')
        self.toolbar.addAction(exitAction)
        self.toolbar.addAction(self.refresh_button)
        self.toolbar.addAction(self.show_history_button)
        self.toolbar.addAction(self.config_btn)

        # Настройки геометрии основного окна
        # Поскольку работать с динамическими размерами мы не умеем, и мало времени на изучение, размер окна фиксирован.
        self.setFixedSize(800, 600)
        self.setWindowTitle('Messaging Server alpha release')

        # Надпись о том, что ниже список подключённых клиентов
        self.label = QLabel('Список подключённых клиентов:', self)
        self.label.setFixedSize(240, 15)
        self.label.move(10, 25)

        # Окно со списком подключённых клиентов.
        self.active_clients_table = QTableView(self)
        self.active_clients_table.move(10, 45)
        self.active_clients_table.setFixedSize(780, 400)
        self.active_clients_table.setModel(self.model)

        # Последним параметром отображаем окно.
        self.show()

    def modelChanged(self):
        self.statusBar().showMessage('Server Working')
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
        self.modelChanged()

    def initUI(self):
        # Настройки окна:
        self.setWindowTitle('Статистика клиентов')
        self.setFixedSize(600, 700)
        # self.setAttribute(Qt. WA_DeleteOnClose)

        # Кнапка закрытия окна
        self.close_button = QPushButton('Закрыть', self)
        self.close_button.move(250, 650)
        self.close_button.clicked.connect(self.controller.hide_stat_window)

        # Лист с собственно историей
        self.history_table = QTableView(self)
        self.history_table.move(10, 10)
        self.history_table.setFixedSize(580, 620)
        self.history_table.setModel(self.model)

    def modelChanged(self):
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
        self.modelChanged()

    def initUI(self):
        # Настройки окна
        self.setFixedSize(500, 160)
        self.setWindowTitle('Настройки сервера')

        # Надпись о файле базы данных:
        self.db_url_label = QLabel('Строка подключения к базе данных: ', self)
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

        # # Кнопка выбора пути.
        # self.db_path_select = QPushButton('Обзор...', self)
        # self.db_path_select.move(275, 28)
        # self.db_path_select.clicked.connect(self.open_file_dialog)

        # # Метка с именем поля файла базы данных
        # self.db_file_label = QLabel('Имя файла базы данных: ', self)
        # self.db_file_label.move(10, 68)
        # self.db_file_label.setFixedSize(180, 15)

        # # Поле для ввода имени файла
        # self.db_file = QLineEdit(self)
        # self.db_file.move(200, 66)
        # self.db_file.setFixedSize(150, 20)

        # Метка с номером порта
        self.port_display_label = QLabel('Порт для соединений (текущий):', self)
        self.port_display_label.move(10, 85)
        self.port_display_label.setFixedSize(300, 20)

        # Поле для номера порта
        self.port_display = QLineEdit(self)
        self.port_display.move(310, 85)
        self.port_display.setFixedSize(200, 20)
        self.port_display.setEnabled(False)

        self.port_display_label = QLabel('Порт для соединений (новый):', self)
        self.port_display_label.move(10, 105)
        self.port_display_label.setFixedSize(300, 20)

        self.port_validator = QIntValidator(EndpointPort.min_value, EndpointPort.max_value, self)
        # Поле для ввода номера порта
        self.port_edit = QLineEdit(self)
        self.port_edit.move(310, 105)
        self.port_edit.setFixedSize(200, 20)
        self.port_edit.setValidator(self.port_validator)
        self.port_edit.textEdited.connect(self.change_port)

        # Кнопка сохранения настроек
        self.save_btn = QPushButton('Сохранить', self)
        self.save_btn.move(190, 130)
        self.save_btn.clicked.connect(self.controller.save_server_config)

        # Кнапка закрытия окна
        self.close_button = QPushButton('Закрыть', self)
        self.close_button.move(275, 130)
        self.close_button.clicked.connect(self.controller.hide_settings_window)

#         self.show()

    # # Функция обработчик открытия окна выбора папки
    # def open_file_dialog(self):
    #     dialog = QFileDialog(self)
    #     path = dialog.getExistingDirectory()
    #     path = path.replace('/', '\\')
    #     self.db_path.insert(path)

    def change_db_url(self):
        self.model.db_url = self.db_url_edit.text()

    def change_port(self):
        self.model.port = self.port_edit.text()

    def modelChanged(self):
        self.db_url_display.setText(self.model.db_url)
        if self.db_url_edit.text() == '':
            self.db_url_edit.setText(self.model.db_url)
        self.port_display.setText(str(self.model.port))
        if self.port_edit.text() == '':
            self.port_edit.setText(str(self.model.port))
