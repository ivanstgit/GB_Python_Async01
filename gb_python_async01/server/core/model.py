"""
Объектная модель сервера.

Модель БД не подходит, т.к. распределена по нескольким таблицам
"""
import datetime
from typing import Optional

from gb_python_async01.transport.model.message import JIMActionMessage


class UserInfo:
    def __init__(self, id, user: str, is_active: bool, status: Optional[str]) -> None:
        self.id = id
        self.user = user
        self.is_active = is_active
        self.status = status


class UserStatistic:
    def __init__(self, user: str, sent: int, received: int) -> None:
        self.user = user
        self.sent = sent
        self.received = received


class UserSessionInfo:
    def __init__(
        self,
        id,
        user: str,
        is_active: bool,
        connected_at: datetime.datetime,
        ip_addr: str,
        ip_port: int,
        pubkey: str,
    ) -> None:
        self.id = id
        self.user = user
        self.is_active = is_active
        self.connected_at = connected_at
        self.ip_addr = ip_addr
        self.ip_port = ip_port
        self.pubkey = pubkey


class MessageInfo:
    def __init__(self, msg_id, action: JIMActionMessage, session_id) -> None:
        self.msg_id = msg_id
        self.action = action
        self.session_id = session_id
