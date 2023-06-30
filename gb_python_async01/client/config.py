import os
from config import BaseConfig
from gb_python_async01.transport.descriptors import EndpointHost, EndpointPort
from gb_python_async01.utils.observer import ObserverNotifier


class ClientConfig(ObserverNotifier):
    """ Config model, supporting changes in runtime """
    port = EndpointPort()
    host = EndpointHost()

    def __init__(self, user_name: str, default_config=BaseConfig):
        self.debug = default_config.DEBUG
        self.testing = default_config.TESTING

        self.user_name = user_name
        self.logger_file_path = os.path.join(default_config.LOG_DIR, f'client_{user_name}.log')
        self.db_url = default_config.CLIENT_DB_URL(user_name)

        self.srv_host = default_config.SERVER_HOST_DEFAULT
        self.srv_port = default_config.SERVER_PORT_DEFAULT
        self.message_max_size = default_config.MESSAGE_MAX_SIZE
