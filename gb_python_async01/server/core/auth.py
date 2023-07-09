from functools import wraps
from typing import Optional

from gb_python_async01.server.core.client_session import ClientSession
from gb_python_async01.server.core.model import UserInfo
from gb_python_async01.server.db.config import ServerStorage
from gb_python_async01.server.db.user_view import UserAuthView
from gb_python_async01.utils.security import PasswordHash


class UserManager():
    """ critical function"""

    def __init__(self, db: ServerStorage) -> None:
        self._db_view = UserAuthView(db)

    def add(self, user_name: str) -> Optional[UserInfo]:
        return self._db_view.add(user_name)

    def set_password(self, user_name: str, password: str) -> Optional[UserInfo]:
        pass_hash = PasswordHash.generate_password_hash(user_name, password)
        return self._db_view.password_set(user_name, pass_hash)
