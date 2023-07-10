class ServerCoreError(Exception):
    def __str__(self):
        return f"Server error"


class ServerCoreNotAuthorizedError(ServerCoreError):
    def __str__(self):
        return f"Not authorized"


class ServerCoreLogout(ServerCoreError):
    def __str__(self):
        return f"Not an error"
