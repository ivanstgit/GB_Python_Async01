import os


class BaseConfig(object):
    DEBUG = False
    TESTING = False

    LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'v_a_r', 'logs')

    SERVER_HOST_DEFAULT = '127.0.0.1'
    SERVER_PORT_DEFAULT = 7777

    SERVER_CONNECTION_LIMIT = 5
    SERVER_TIMEOUT = 0.5

    SERVER_DB_URL = 'sqlite:///server_base.db3'
    @staticmethod
    def CLIENT_DB_URL(user): return f'sqlite:///client_{user}_base.db3'

    MESSAGE_MAX_SIZE = 4096

    ANONIMOUS_USER = 'guest'


class DevConfig(BaseConfig):
    DEBUG = True


class TestingConfig(BaseConfig):
    TESTING = True
