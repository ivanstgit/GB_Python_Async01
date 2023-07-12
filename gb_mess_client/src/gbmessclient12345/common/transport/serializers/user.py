from gbmessclient12345.common.transport.errors import JIMValidationError
from gbmessclient12345.common.transport.model.user import JIMUser


class JIMUserSerializer:
    @staticmethod
    def from_dict(us: dict) -> JIMUser:
        username = us.get(JIMUserSerializer.Const.username)
        is_active = us.get(JIMUserSerializer.Const.is_active) or False
        status = us.get(JIMUserSerializer.Const.status)
        last_login = us.get(JIMUserSerializer.Const.last_login)
        pubkey = us.get(JIMUserSerializer.Const.pubkey)
        if username and last_login and pubkey:
            return JIMUser(username, is_active, status, last_login, pubkey)

        raise JIMValidationError()

    @staticmethod
    def to_dict(us: JIMUser) -> dict:
        return {
            JIMUserSerializer.Const.username: us.username,
            JIMUserSerializer.Const.is_active: us.is_active,
            JIMUserSerializer.Const.status: us.status,
            JIMUserSerializer.Const.last_login: us.last_login,
            JIMUserSerializer.Const.pubkey: us.pubkey,
        }

    class Const:
        username = "username"
        is_active = "is_active"
        status = "status"
        last_login = "last_login"
        pubkey = "pubkey"
