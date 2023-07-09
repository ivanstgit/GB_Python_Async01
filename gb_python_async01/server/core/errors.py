class ServerError(Exception):
    def __str__(self):
        return f'Server error'


class ServerNotAuthorized(ServerError):
    def __str__(self):
        return f'Not authorized'


class ServerLogout(ServerError):
    def __str__(self):
        return f'Not an error'
