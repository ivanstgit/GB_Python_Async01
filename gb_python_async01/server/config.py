import os
from config import BaseConfig
from gb_python_async01.transport.descriptors import EndpointHost, EndpointPort
from gb_python_async01.utils.observer import ObserverNotifier


class ServerConfig(ObserverNotifier):
    """ Config model, supporting changes in runtime """
    port = EndpointPort()
    host = EndpointHost()

    def __init__(self, default_config=BaseConfig):
        self.debug = default_config.DEBUG
        self.testing = default_config.TESTING

        self.logger_name = 'server'
        self.logger_file_path = os.path.join(default_config.LOG_DIR, 'server.log')

        self.db_url = default_config.SERVER_DB_URL

        self.host = default_config.SERVER_HOST_DEFAULT
        self.port = default_config.SERVER_PORT_DEFAULT
        self.message_max_size = default_config.MESSAGE_MAX_SIZE
        self.connection_limit = default_config.SERVER_CONNECTION_LIMIT
        self.timeout = default_config.SERVER_TIMEOUT
