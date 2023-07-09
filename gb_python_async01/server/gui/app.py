# Графический интерфейс сервера, запускается в отдельном треде
import sys
import threading

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QApplication

from gb_python_async01.server.db.config import ServerStorage
from gb_python_async01.server.gui.controller import ServerGUIController
from gb_python_async01.server.gui.model import *
from gb_python_async01.server.gui.view import *


class ServerGUI():

    def __init__(self, config: ServerConfig, db: ServerStorage, config4edit: ServerConfig) -> None:
        self.db = db
        self.config = config
        self.config_editable = config4edit

    def run(self, config_changed: threading.Event, terminate_on: threading.Event):
        server_app = QApplication(sys.argv)

        active_users_model = ActiveUsersModel(self.db)
        user_statistics_model = UserStatisticsModel(self.db)
        settings_model = SettingsModel(self.config_editable)
        user_model = UserModel(self.db)
        selected_user_model = SingleSelectionModel()

        controller = ServerGUIController(config_changed, self.config, settings_model)

        main_window = MainWindow(active_users_model, controller)
        controller.addObserver(main_window)
        stat_window = StatisticsWindow(user_statistics_model, controller)
        controller.register_stat_window(stat_window)
        controller.addObserver(stat_window)
        settings_window = SettingsWindow(settings_model, controller)
        controller.register_settings_window(settings_window)
        user_window = UserWindow(user_model, selected_user_model, controller)
        controller.register_user_window(user_window)

        timer = QTimer()
        timer.timeout.connect(lambda: self._on_timer(server_app, controller, terminate_on))
        timer.start(1000)

        server_app.exec_()
        timer.stop()

    def _on_timer(self, qapp: QApplication, controller: ServerGUIController, terminate_on: threading.Event):
        if terminate_on.isSet():
            qapp.closeAllWindows()
        else:
            controller.notifyObservers()
