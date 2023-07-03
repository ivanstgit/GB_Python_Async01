# Модели с данными для GUI. Т.к. в проекте исползуется SQLAlchemy, то это скорее интеграционная прослойка
from copy import copy
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from gb_python_async01.server.config import ServerConfig

from gb_python_async01.server.db.view import ActiveUser, ServerStorage
from gb_python_async01.transport.descriptors import EndpointHost, EndpointPort


class ActiveUsersModel(QStandardItemModel):

    def __init__(self, db: ServerStorage):
        super().__init__()
        self.db = db
        self.refresh()

    def refresh(self):
        data = self.db.gui_get_active_user_list()
        self.clear()
        self.setHorizontalHeaderLabels(['Имя Клиента', 'IP Адрес', 'Порт', 'Время подключения'])
        for line in data:
            au = line
            self.appendRow([self._get_item(au.user),
                            self._get_item(au.ip_addr),
                            self._get_item(au.ip_port),
                            self._get_item(au.connected_at),
                            ])

    def _get_item(self, value):
        item = QStandardItem(str(value))
        item.setEditable(False)
        return item


class UserStatisticsModel(QStandardItemModel):

    def __init__(self, db: ServerStorage):
        super().__init__()
        self.db = db
        self.refresh()

    def refresh(self):
        data = self.db.gui_user_get_statistics()
        self.clear()
        self.setHorizontalHeaderLabels(['Имя Клиента', 'Отправлено', 'Получено'])
        for line in data:
            us = line
            self.appendRow([self._get_item(us.user),
                            self._get_item(us.sent),
                            self._get_item(us.received)
                            ])

    def _get_item(self, value):
        item = QStandardItem(str(value))
        item.setEditable(False)
        return item


class SettingsModel():
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
