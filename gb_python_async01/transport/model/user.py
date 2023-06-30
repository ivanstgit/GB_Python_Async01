class User():
    def __init__(self, username, is_active=False, status=None, last_login=None) -> None:
        self.username = username
        self.is_active = is_active
        self.status = status
        self.last_login = last_login
