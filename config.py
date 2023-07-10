import os

import sqlalchemy


class BaseConfig(object):
    DEBUG = False
    TESTING = False

    VAR_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "v_a_r")

    SERVER_HOST_DEFAULT = "127.0.0.1"
    SERVER_PORT_DEFAULT = 7777

    SERVER_CONNECTION_LIMIT = 5
    SERVER_TIMEOUT = 0.5

    SERVER_DB_URL = os.environ.get("DB_URL")
    MESSAGE_MAX_SIZE = 4096


class DevConfig(BaseConfig):
    DEBUG = True


class TestingConfig(BaseConfig):
    TESTING = True

    TEST_USER = "ttttest"
    TEST_PASSWORD = "ttttest"
