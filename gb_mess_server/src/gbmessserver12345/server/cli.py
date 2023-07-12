"""Инструменты командной строки для обработки консольных команд"""
from gbmessserver12345.server.config import ServerConfig
from gbmessserver12345.server.core.auth import UserManager
from gbmessserver12345.server.db.config import ServerStorage
from gbmessserver12345.server.logger import ServerLogger


class ServerCLI:
    """Server Administration:
    Only for migration and testing
    """

    def __init__(self, config: ServerConfig):
        self.config = config
        self.logger = ServerLogger(
            self.config.logger_file_path, self.config.debug, self.config.testing
        ).logger
        self.db = ServerStorage(self.config.db_url)

    def init_db_tables(self):
        self.logger.warning("CLI - init tables")
        self.db.adm_init_db_tables()
        print("DB tables created")

    def add_user(self, login: str, password: str):
        self.logger.warning("CLI - add_user login")
        um = UserManager(self.db)
        try:
            um.add(login)
            um.set_password(login, password)
        except Exception as e:
            print(f"error {e}")
        else:
            print(f"user {login} added")
