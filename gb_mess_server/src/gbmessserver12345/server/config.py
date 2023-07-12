"""Конфигурация сервера"""
import os

from sqlalchemy import URL

from gbmessserver12345.common.transport.descriptors import EndpointHost, EndpointPort
from gbmessserver12345.common.utils.observer import ObserverNotifier

SERVER_HOST_DEFAULT = "127.0.0.1"
SERVER_PORT_DEFAULT = 7777

SERVER_CONNECTION_LIMIT = 5
SERVER_TIMEOUT = 0.5

MESSAGE_MAX_SIZE = 4096


class ServerConfig(ObserverNotifier):
    """Config model, supporting changes in runtime"""

    port = EndpointPort()
    host = EndpointHost()

    def __init__(self, root_dir: str, debug=False, testing=False):
        self.debug = debug
        self.testing = testing

        self.var_dir = self._check_or_init_dir(os.path.join(root_dir, "var"))
        self.log_dir = self._check_or_init_dir(os.path.join(self.var_dir, "log"))
        self.db_dir = self._check_or_init_dir(os.path.join(self.var_dir, "db"))

        self.logger_name = "server"
        self.logger_file_path = os.path.join(self.log_dir, "server.log")

        self.db_url = os.environ.get("DB_URL") or str(
            URL.create(
                "sqlite",
                database=os.path.join(self.db_dir, "server_base.db3"),
            )
        )

        self.host = SERVER_HOST_DEFAULT
        self.port = SERVER_PORT_DEFAULT

        self.message_max_size = MESSAGE_MAX_SIZE
        self.connection_limit = SERVER_CONNECTION_LIMIT
        self.timeout = SERVER_TIMEOUT

        self.gui_enabled = True

    @staticmethod
    def _check_or_init_dir(dir: str) -> str:
        if not os.path.exists(dir):
            os.mkdir(dir)
        return dir
