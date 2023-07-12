"""Сериализаторы (БД/транспорт/сервер)"""
import datetime

from gbmessserver12345.server.core.model import UserInfo, UserSessionInfo, MessageInfo
from gbmessserver12345.server.db.model import User, UserSession, Message
from gbmessserver12345.common.transport.model.message import JIMActionMessage
from gbmessserver12345.common.transport.model.user import JIMUser


class UserSerializer:
    """Пользователь"""

    @staticmethod
    def from_db(user: User) -> UserInfo:
        if user.status:
            status = user.status.status  # type: ignore
        else:
            status = None
        return UserInfo(
            id=user.id, user=user.name, is_active=user.is_active, status=status
        )


class UserSessionSerializer:
    @staticmethod
    def from_db(user_last_session: UserSession) -> UserSessionInfo:
        return UserSessionInfo(
            id=user_last_session.id,
            user=user_last_session.user.name,
            is_active=user_last_session.is_active,
            connected_at=user_last_session.created_at,
            ip_addr=user_last_session.ip,
            ip_port=user_last_session.port,
            pubkey=user_last_session.pubkey,
        )

    @staticmethod
    def to_transport(us: UserInfo, si: UserSessionInfo) -> JIMUser:
        return JIMUser(
            username=us.user,
            is_active=si.is_active,
            status=us.status,
            last_login=si.connected_at.timestamp(),
            pubkey=si.pubkey,
        )


class MessageSerializer:
    @staticmethod
    def from_db(msg: Message) -> MessageInfo:
        am = JIMActionMessage(
            time=msg.created_at.timestamp(),
            sender=msg.sender.name,
            receiver=msg.receiver.name,
            message=msg.msg_txt,
        )
        return MessageInfo(msg_id=msg.id, action=am, session_id=msg.sender_session_id)

    @staticmethod
    def to_db(sender: User, receiver: User, message: MessageInfo) -> Message:
        msg = message.action
        return Message(
            id=message.msg_id,
            created_at=datetime.datetime.fromtimestamp(msg.time),
            sender_id=sender.id,
            receiver_id=receiver.id,
            msg_txt=msg.message,
            sender_session_id=message.session_id,
        )
