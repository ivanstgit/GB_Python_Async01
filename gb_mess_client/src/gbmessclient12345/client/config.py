"""Конфигурация клиента"""
import os

from sqlalchemy import URL

from gbmessclient12345.common.transport.descriptors import EndpointHost, EndpointPort
from gbmessclient12345.common.utils.observer import ObserverNotifier

SERVER_HOST_DEFAULT = "127.0.0.1"
SERVER_PORT_DEFAULT = 7777

MESSAGE_MAX_SIZE = 4096


class ClientConfig(ObserverNotifier):
    """Config model, supporting changes in runtime"""

    port = EndpointPort()
    host = EndpointHost()

    def __init__(self, root_dir: str, debug=False, testing=False):
        self.debug = debug
        self.testing = testing

        self.srv_host = SERVER_HOST_DEFAULT
        self.srv_port = SERVER_PORT_DEFAULT
        self.message_max_size = MESSAGE_MAX_SIZE

        self.var_dir = self._check_or_init_dir(os.path.join(root_dir, "var"))
        self.log_dir = self._check_or_init_dir(os.path.join(self.var_dir, "log"))
        self.db_dir = self._check_or_init_dir(os.path.join(self.var_dir, "db"))
        self.key_dir = self._check_or_init_dir(os.path.join(self.var_dir, "key"))

        self.logger_file_path = os.path.join(self.log_dir, "client.log")

    def after_login(self, user_name: str):
        self.user_name = user_name
        self.logger_file_path = os.path.join(self.log_dir, f"client_{user_name}_.log")

        self.db_url = URL.create(
            "sqlite",
            database=os.path.join(self.db_dir, f"client_{user_name}_base.db3"),
        )

    @staticmethod
    def _check_or_init_dir(dir: str) -> str:
        if not os.path.exists(dir):
            os.mkdir(dir)
        return dir
