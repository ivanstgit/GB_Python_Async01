"""Конфигурация и общие функции для работы с БД"""
import threading

from sqlalchemy import create_engine
from sqlalchemy.dialects import sqlite

from gbmessserver12345.server.db.model import Base


class ServerStorage:
    def __init__(self, db_url) -> None:
        self.db_engine = create_engine(db_url, echo=False, pool_recycle=7200)
        self.lock = threading.Lock()

    def adm_init_db_tables(self):
        Base.metadata.create_all(self.db_engine)

    def stop(self):
        self.db_engine.dispose()


class ServerDBBaseView:
    """Базовый класс для классов доступа к данным БД"""

    def __init__(self, db: ServerStorage) -> None:
        self.db = db
        self.db_engine = db.db_engine
