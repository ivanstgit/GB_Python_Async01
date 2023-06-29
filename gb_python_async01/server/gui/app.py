import sys
import threading
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import (QAction, QApplication, QDialog, QFileDialog,
                             QLabel, QLineEdit, QMainWindow, QMessageBox,
                             QPushButton, QTableView, qApp)
from gb_python_async01.server.db.view import ServerStorage
from gb_python_async01.server.gui.controller import ServerGUIController
from gb_python_async01.server.gui.model import *

from gb_python_async01.server.gui.view import *


class ServerGUI():

    def __init__(self, config: ServerConfig, db: ServerStorage) -> None:
        self.db = db
        self.config = config

    def run(self, config_changed: threading.Event):
        server_app = QApplication(sys.argv)

        active_users_model = ActiveUsersModel(self.db)
        user_statistics_model = UserStatisticsModel(self.db)
        settings_model = SettingsModel(self.config)

        controller = ServerGUIController(config_changed, self.config)

        main_window = MainWindow(active_users_model, controller)
        controller.addObserver(main_window)
        stat_window = StatisticsWindow(user_statistics_model, controller)
        controller.register_stat_window(stat_window)
        settings_window = SettingsWindow(settings_model, controller)
        controller.register_settings_window(settings_window)

        timer = QTimer()
        timer.timeout.connect(controller.notifyObservers)
        timer.start(1000)

        server_app.exec_()
        timer.stop()
