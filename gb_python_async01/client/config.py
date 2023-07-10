"""Конфигурация клиента"""
import os

from sqlalchemy import URL

from config import BaseConfig
from gb_python_async01.transport.descriptors import EndpointHost, EndpointPort
from gb_python_async01.utils.observer import ObserverNotifier


class ClientConfig(ObserverNotifier):
    """Config model, supporting changes in runtime"""

    port = EndpointPort()
    host = EndpointHost()

    def __init__(self, default_config=BaseConfig):
        self.debug = default_config.DEBUG
        self.testing = default_config.TESTING
        self.srv_host = default_config.SERVER_HOST_DEFAULT
        self.srv_port = default_config.SERVER_PORT_DEFAULT
        self.message_max_size = default_config.MESSAGE_MAX_SIZE
        self.var_dir = default_config.VAR_DIR
        self.logger_file_path = os.path.join(self.var_dir, "log", f"client.log")

    def after_login(self, user_name: str):
        self.user_name = user_name
        self.logger_file_path = os.path.join(
            self.var_dir, "log", f"client_{user_name}_.log"
        )

        self.db_url = URL.create(
            "sqlite",
            database=os.path.join(self.var_dir, "db", f"client_{user_name}_base.db3"),
        )
