"""Исключения при работе с БД"""


class ServerDBError(Exception):
    def __init__(self, *args: object, msg="") -> None:
        super().__init__(*args)
        self._msg = msg

    def __str__(self):
        if self._msg:
            return f"DB error: {self._msg}"

        return f"DB error"


class ServerDBUserNotExists(ServerDBError):
    def __str__(self):
        return f"User not exists"


class ServerDBUserAlreadyExists(ServerDBError):
    def __str__(self):
        return f"User already exists"


class ServerDBUserSessionNotExists(ServerDBError):
    def __str__(self):
        return f"User session not exists"
