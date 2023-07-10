""" Модели с данными для GUI. Т.к. в проекте исползуется SQLAlchemy, то это скорее интеграционная прослойка"""
from copy import copy
from typing import List, Optional

from PyQt5.QtGui import QStandardItem, QStandardItemModel

from gb_python_async01.server.config import ServerConfig
from gb_python_async01.server.core.auth import UserManager
from gb_python_async01.server.core.model import UserInfo
from gb_python_async01.server.db.config import ServerStorage
from gb_python_async01.server.db.view import MessageView, UserSessionView, UserView
from gb_python_async01.transport.descriptors import EndpointPort
from gb_python_async01.utils.observer import ObserverNotifier
from gb_python_async01.utils.security import PasswordHash


class ActiveUsersModel(QStandardItemModel):
    """Модель для таблицы активных пользователей"""

    def __init__(self, db: ServerStorage):
        super().__init__()
        self.db_view = UserSessionView(db)

        self.refresh()

    def refresh(self):
        """Обновить данные в модели"""
        data = self.db_view.get_list()
        self.clear()
        self.setHorizontalHeaderLabels(
            ["Имя Клиента", "IP Адрес", "Порт", "Время подключения"]
        )
        for au in data:
            self.appendRow(
                [
                    self._get_item(au.user),
                    self._get_item(au.ip_addr),
                    self._get_item(au.ip_port),
                    self._get_item(au.connected_at),
                ]
            )

    def _get_item(self, value):
        item = QStandardItem(str(value))
        item.setEditable(False)
        return item


class UserStatisticsModel(QStandardItemModel):
    """Модель для таблицы статистики пользователей"""

    def __init__(self, db: ServerStorage):
        super().__init__()
        self.db = db
        self.db_view = MessageView(db)
        self.refresh()

    def refresh(self):
        data = self.db_view.gui_user_get_statistics()
        self.clear()
        self.setHorizontalHeaderLabels(["Имя Клиента", "Отправлено", "Получено"])
        for line in data:
            us = line
            self.appendRow(
                [
                    self._get_item(us.user),
                    self._get_item(us.sent),
                    self._get_item(us.received),
                ]
            )

    def _get_item(self, value):
        item = QStandardItem(str(value))
        item.setEditable(False)
        return item


class SettingsModel:
    port = EndpointPort

    def __init__(self, config4edit: ServerConfig) -> None:
        self._config_orig = copy(config4edit)
        self._config = config4edit
        self.db_url = self._config.db_url
        self.port = str(self._config.port)

    def restore(self):
        self._config = self._config_orig

    def apply_config_changes(self):
        self._config.db_url = self.db_url
        self._config.port = int(self.port)  # type: ignore


class SingleSelectionModel(ObserverNotifier):
    def __init__(self) -> None:
        super().__init__()
        self.selected = None

    def set_selected(self, selected):
        if selected != self.selected:
            if (not selected) or selected == "":
                self.selected = None
            else:
                self.selected = selected
            self.notify_observers()


class UserModel(QStandardItemModel, ObserverNotifier):
    users: List[UserInfo]

    def __init__(self, db: ServerStorage):
        super().__init__()
        self.db = db
        self.db_view = UserView(db)
        self.um = UserManager(db)
        self.refresh()

    def refresh(self):
        self.users = self.db_view.get_list(only_active=False)
        self.clear()
        self.setHorizontalHeaderLabels(["Логин", "Активен"])
        for us in self.users:
            self.appendRow([self._get_item(us.user), self._get_item(us.is_active)])
        self.notify_observers()

    def get_user_in_row(self, row_index: int) -> str:
        if row_index < self.rowCount():
            res = self.item(row_index, 0).text()
            return res
        return ""

    def set_password(self, user_name, password) -> Optional[str]:
        if not password or password == "":
            return "Invalid password!"

        try:
            pass_hash = PasswordHash.generate_password_hash(user_name, password)
            self.um.set_password(user_name, pass_hash)
        except Exception as e:
            return f"Error {e}"

        self.refresh()
        return None

    def add_user(self, user_name, password) -> Optional[str]:
        if not password or password == "":
            return "Invalid password!"

        is_exists = sum([user.user == user_name for user in self.users])
        if is_exists:
            return "User already exist!"

        try:
            pass_hash = PasswordHash.generate_password_hash(user_name, password)
            self.um.add(user_name)
            self.um.set_password(user_name, pass_hash)
        except Exception as e:
            return f"Error {e}"

        self.refresh()
        return None

    def _get_item(self, value):
        item = QStandardItem(str(value))
        item.setEditable(False)
        return item
