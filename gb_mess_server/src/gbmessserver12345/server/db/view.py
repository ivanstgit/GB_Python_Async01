"""Классы для чтения/записи в БД"""
"""Методы для работы с данными пользователей"""
import datetime
from typing import List, Optional, Union

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from gbmessserver12345.server.core.model import (
    MessageInfo,
    UserInfo,
    UserSessionInfo,
    UserStatistic,
)
from gbmessserver12345.server.core.serializers import (
    MessageSerializer,
    UserSerializer,
    UserSessionSerializer,
)
from gbmessserver12345.server.db.config import ServerDBBaseView, ServerStorage
from gbmessserver12345.server.db.errors import *
from gbmessserver12345.server.db.errors import (
    ServerDBError,
    ServerDBUserAlreadyExists,
    ServerDBUserNotExists,
)
from gbmessserver12345.server.db.model import (
    Message,
    User,
    UserContact,
    UserPrivate,
    UserSession,
    UserStatus,
    extpk,
)


class UserAuthView(ServerDBBaseView):
    """Класс для работы с пользователями (критические операции)"""

    def add(self, user_name: str) -> UserInfo:
        with self.db.lock, Session(self.db_engine) as session:
            user = self._user_get(session, user_name)
            if user:
                raise ServerDBUserAlreadyExists
            user = User(id=None, name=user_name, is_active=True)
            session.add(user)
            session.commit()
            return UserSerializer.from_db(user)

    def password_set(self, user_name: str, password_hash: str):
        with self.db.lock, Session(self.db_engine) as session:
            user = self._user_get(session, user_name)
            if not user:
                raise ServerDBUserNotExists
            if not user.is_active:
                user.activate()
                session.add(user)

            up = self._password_set(session, user, password_hash)
            session.add(up)
            session.commit()
            return UserSerializer.from_db(user)

    def password_get(self, user_name: str, only_active=True) -> Union[str, None]:
        with Session(self.db_engine) as session:
            user = self._user_get(session, user_name)
            if not user:
                return None
            if only_active and not user.is_active:
                return None

            user_id = user.id

            stmt = select(UserPrivate.password).where(UserPrivate.user_id == user_id)
            return session.scalars(stmt).first()

    def _user_get(self, session: Session, user_name: str) -> Union[User, None]:
        return session.query(User).filter_by(name=user_name).first()

    def _user_add(self, session: Session, user_name: str) -> User:
        """Warning! Check user existence before using"""
        user = User(id=None, name=user_name)
        session.add(user)
        return user

    def _password_set(
        self, session: Session, user: User, password_hash: str
    ) -> UserPrivate:
        """Warning! Check user existence before using"""
        up = session.query(UserPrivate).filter_by(user=user).first()
        if up:
            up.password = password_hash
            up.updated_at = datetime.datetime.now()
        else:
            up = UserPrivate(id=None, user=user, password=password_hash)
        session.add(up)
        return up


class UserView(ServerDBBaseView):
    def get(self, user_name: str, only_active=True) -> Union[UserInfo, None]:
        with Session(self.db_engine) as session:
            user = self._user_get(session, user_name)
            if not user:
                return None
            if only_active and not user.is_active:
                return None
            return UserSerializer.from_db(user)

    def get_list(self, only_active=True) -> List[UserInfo]:
        with Session(self.db_engine) as session:
            result = []
            stmt = select(User).join(UserStatus, isouter=True)
            users = session.scalars(stmt).fetchall()
            if not users:
                return result
            result = [
                UserSerializer.from_db(user)
                for user in users
                if only_active and user.is_active or not only_active
            ]
        return list(result)

    def contact_add(self, user_name, contact_name) -> UserInfo:
        with self.db.lock, Session(self.db_engine) as session:
            user = self._user_get(session, user_name)
            if not user:
                raise ServerDBUserNotExists
            contact = self._user_get(session, contact_name)
            if not contact:
                raise ServerDBUserNotExists
            user_contact = self._user_contact_get(session, user, contact)
            if user_contact:
                user_contact.activate()
            else:
                user_contact = self._user_contact_add(session, user, contact)
            session.add(user_contact)
            session.commit()
            return UserSerializer.from_db(contact)

    def contact_delete(self, user_name, contact_name) -> None:
        with self.db.lock, Session(self.db_engine) as session:
            user = self._user_get(session, user_name)
            if not user:
                raise ServerDBUserNotExists
            contact = self._user_get(session, contact_name)
            if not contact:
                raise ServerDBUserNotExists
            user_contact = self._user_contact_get(session, user, contact)
            if user_contact:
                user_contact.deactivate()
                session.add(user_contact)
                session.commit()

    def contact_get_list(self, user_name: str) -> Union[List[UserInfo], None]:
        with self.db.lock, Session(self.db_engine) as session:
            user = self._user_get(session, user_name)
            if not user:
                raise ServerDBUserNotExists
            if not user.is_active:
                raise ServerDBUserNotExists
            stmt_contacts = (
                select(User)
                .join(UserContact, UserContact.contact_id == User.id)
                .where(
                    UserContact.user_id == user.id,
                    UserContact.is_active == True,
                    User.is_active == True,
                )
            )
            contacts = session.scalars(stmt_contacts).fetchall()
            if not contacts:
                return None
        result = [self.get(contact.name) for contact in contacts]

        return list(result)  # type: ignore

    def status_update(self, user_name, status: str):
        with self.db.lock, Session(self.db_engine) as session:
            user = self._user_get(session, user_name)
            if not user:
                raise ServerDBUserNotExists

            stmt = (
                select(UserStatus).join(User).where(User.id == user.id, User.is_active)
            )
            us = session.scalars(stmt).first()
            if us:
                us.status = status
                us.updated_at = datetime.datetime.now()
            else:
                us = UserStatus(id=None, user_id=user.id, status=status)
            session.add(us)
            session.commit()

    def _user_get(self, session: Session, user_name: str) -> Union[User, None]:
        return session.query(User).filter_by(name=user_name).first()

    def _user_contact_get(
        self, session: Session, user: User, contact: User
    ) -> Union[UserContact, None]:
        return (
            session.query(UserContact)
            .filter_by(contact_id=contact.id, user_id=user.id)
            .first()
        )

    def _user_contact_add(
        self, session: Session, user: User, contact: User
    ) -> UserContact:
        """Warning! Check user existence before using"""
        user_contact = UserContact(id=None, user_id=user.id, contact_id=contact.id)
        session.add(user_contact)
        return user_contact


class UserSessionView(ServerDBBaseView):
    def __init__(self, db: ServerStorage) -> None:
        super().__init__(db)

    def _user_get(self, session: Session, user_name: str) -> Union[User, None]:
        return session.query(User).filter_by(name=user_name).first()

    def _get_last(self, session: Session, user: User) -> Union[UserSession, None]:
        return (
            session.query(UserSession).filter_by(user_id=user.id, is_last=True).first()
        )

    def _add(self, session: Session, user: User, ip, port, pubkey) -> UserSession:
        user_session_prev = self._get_last(session, user)
        if user_session_prev:
            user_session_prev.is_active = False
            user_session_prev.is_last = False
            user_session_prev.updated_at = datetime.datetime.now()
            session.add(user_session_prev)

        user_session_curr = UserSession(
            user_id=user.id,
            ip=ip,
            port=port,
            is_active=True,
            is_last=True,
            pubkey=pubkey,
        )
        session.add(user_session_curr)
        return user_session_curr

    # client integration (integration model format, in new sessions)
    def clear_active_connections(self):
        with Session(self.db_engine) as session, self.db.lock:
            stmt_user_sessions_active = (
                select(UserSession)
                .where(UserSession.is_active == True)
                .group_by(UserSession.user_id)
            )
            user_sessions_active = session.scalars(stmt_user_sessions_active).fetchall()

            for user_session in user_sessions_active:
                user_session.deactivate()
                session.add(user_session)
            session.commit()

    def login(self, user_name: str, ip, port, pubkey) -> extpk:
        with Session(self.db_engine) as session, self.db.lock:
            user = self._user_get(session, user_name)
            if not user:
                raise ServerDBUserNotExists
            user_session = self._add(session, user, ip, port, pubkey)
            session.add(user_session)
            session.commit()
            return user_session.id

    def logout(self, user_name: str) -> None:
        with Session(self.db_engine) as session, self.db.lock:
            user = self._user_get(session, user_name)
            if not user:
                raise ServerDBUserNotExists
            last_session = self._get_last(session, user)
            if not last_session:
                raise ServerDBUserSessionNotExists
            last_session.deactivate()
            session.add(last_session)
            session.commit()

    def get_last(self, user_name: str) -> Optional[UserSessionInfo]:
        with Session(self.db_engine) as session:
            user = self._user_get(session, user_name)
            if not user:
                raise ServerDBUserNotExists
            ls = self._get_last(session, user)
            if ls:
                return UserSessionSerializer.from_db(ls)
            return None

    def get_list(self) -> List[UserSessionInfo]:
        result = []
        with Session(self.db_engine) as session:
            stmt_users_active_logins = (
                select(UserSession)
                .join(User)
                .where(UserSession.is_active == True)
                .group_by(UserSession.user_id)
            )
            users_active_logins = session.scalars(stmt_users_active_logins).fetchall()

            for _ in users_active_logins:
                active_user = UserSessionSerializer.from_db(_)

                result.append(active_user)
        return result


class MessageView(ServerDBBaseView):
    """Класс с методами обработки сообщений в БД"""

    def _user_get(self, session: Session, user_name: str) -> Union[User, None]:
        return session.query(User).filter_by(name=user_name).first()

    def add(self, msg: MessageInfo) -> MessageInfo:
        with self.db.lock, Session(self.db_engine) as session:
            sender = session.query(User).filter_by(name=msg.action.sender).first()
            receiver = session.query(User).filter_by(name=msg.action.receiver).first()
            if sender and receiver:
                message = MessageSerializer.to_db(sender, receiver, msg)
                session.add(message)
                session.commit()
                return MessageSerializer.from_db(message)
            raise ServerDBError("Sender or receiver not found")

    def set_delivered(self, msg: MessageInfo) -> None:
        with self.db.lock:
            with Session(self.db_engine) as session:
                message = session.query(Message).filter_by(id=msg.msg_id).first()
                if message:
                    message.is_delivered = True
                    session.add(message)
                    session.commit()
                else:
                    raise ServerDBError("Message not found")

    def get_undelivered_list(self, receiver_name: str) -> List[MessageInfo]:
        with Session(self.db_engine) as session:
            receiver = self._user_get(session, user_name=receiver_name)
            stmt = (
                select(Message)
                .join(User, Message.sender_id == User.id)
                .where(
                    Message.is_delivered == False,
                    Message.receiver == receiver,
                    User.is_active == True,
                )
                .order_by(Message.created_at)
            )
            msgs = session.scalars(stmt).fetchall()
            if not msgs:
                return []
            result = [MessageSerializer.from_db(msg) for msg in msgs]
        return list(result)

    def gui_user_get_statistics(self) -> List[UserStatistic]:
        result = []
        with Session(self.db_engine) as session:
            stmt_users = select(User)
            stmt_mesg_sent = select(Message.sender_id, func.count(Message.id)).group_by(
                Message.sender_id
            )
            stmt_mesg_received = select(
                Message.receiver_id, func.count(Message.id)
            ).group_by(Message.receiver_id)
            users = session.scalars(stmt_users).fetchall()
            messages_sent = session.execute(stmt_mesg_sent).fetchall()
            messages_received = session.execute(stmt_mesg_received).fetchall()

            for user in users:
                sent = sum([line[1] for line in messages_sent if line[0] == user.id])
                received = sum(
                    [line[1] for line in messages_received if line[0] == user.id]
                )
                stat = UserStatistic(user=user.name, sent=sent, received=received)
                result.append(stat)
        return result
