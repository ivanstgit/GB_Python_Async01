"""Модуль с общими классами серверных исключений"""


class ServerError(Exception):
    """Базовый класс исключений"""

    def __str__(self):
        return self.__doc__ or self.__class__.__name__


class ServerNoDBError(ServerError):
    """База данных не инициализирована"""
