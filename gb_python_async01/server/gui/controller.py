# Обработчик событий (сигналов) между окнами/приложением
import threading
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, qApp
from gb_python_async01.server.config import ServerConfig
from gb_python_async01.server.gui.model import *

from gb_python_async01.utils.observer import ObserverNotifier


class ServerGUIController(ObserverNotifier):
    def __init__(self, config_changed: threading.Event, config: ServerConfig, config_model: SettingsModel) -> None:
        super().__init__()
        self.config = config
        self.config_model = config_model
        self.config_changed_event = config_changed
        self.stat_window = None
        self.settings_window = None

    def show_stat_window(self):
        if self.stat_window:
            self.stat_window.show()

    def hide_stat_window(self):
        if self.stat_window:
            self.stat_window.hide()

    def show_settings_window(self):
        if self.settings_window:
            self.settings_window.show()

    def hide_settings_window(self):
        if self.settings_window:
            self.settings_window.hide()

    def save_server_config(self):
        self.config_model.apply_config_changes()
        self.config_changed_event.set()
        self.app_quit()

    # def register_main_window(self, window: QWidget):
    #     self.main_window = window

    def register_stat_window(self, window: QWidget):
        self.stat_window = window

    def register_settings_window(self, window: QWidget):
        self.settings_window = window

    def app_quit(self):
        qApp.quit()
