

class BaseConfig(object):
    DEBUG = False
    TESTING = False

    SERVER_HOST_DEFAULT = '127.0.0.1'
    SERVER_PORT_DEFAULT = 7777

    CONNECTION_LIMIT = 5

    MESSAGE_MAX_SIZE = 4096


class DevConfig(BaseConfig):
    DEBUG = True


class TestingConfig(BaseConfig):
    TESTING = True
