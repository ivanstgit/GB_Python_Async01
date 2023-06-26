

class BaseConfig(object):
    DEBUG = False
    TESTING = False

    SERVER_HOST_DEFAULT = '127.0.0.1'
    SERVER_PORT_DEFAULT = 7777

    SERVER_CONNECTION_LIMIT = 5
    SERVER_TIMEOUT = 0.5

    SERVER_DB_URL = 'sqlite:///server_base.db3'

    MESSAGE_MAX_SIZE = 4096

    ANONIMOUS_USER = 'guest'


class DevConfig(BaseConfig):
    DEBUG = True


class TestingConfig(BaseConfig):
    TESTING = True
