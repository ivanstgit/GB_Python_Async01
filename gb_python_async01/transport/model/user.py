from typing import Optional


class JIMUser():
    def __init__(self, username: str, is_active: bool, status: Optional[str], last_login: float, pubkey: str) -> None:
        self.username = username
        self.is_active = is_active
        self.status = status
        self.last_login = last_login
        self.pubkey = pubkey

    def __str__(self) -> str:
        return f'User {self.username}'
