
import datetime
import time
from typing import List, Union
from sqlalchemy import create_engine, select, update
from sqlalchemy.orm import Session
from gb_python_async01.server.core.model import UserInfo
from gb_python_async01.server.core.serializers import UserSerializer
from gb_python_async01.server.db.config import ServerDBBaseView, ServerStorage

from gb_python_async01.server.db.model import User, UserStatus, UserPrivate, UserContact, extpk
from gb_python_async01.server.db.errors import *


class UserAuthView(ServerDBBaseView):
    def __init__(self, db: ServerStorage) -> None:
        super().__init__(db)

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

    def _user_get(self, session: Session, user_name: str) -> Union[User, None]:
        return session.query(User).filter_by(name=user_name).first()

    def _user_add(self, session: Session, user_name: str) -> User:
        """ Warning! Check user existence before using """
        user = User(id=None, name=user_name)
        session.add(user)
        return user

    def _password_set(self, session: Session, user: User, password_hash: str) -> UserPrivate:
        """ Warning! Check user existence before using """
        up = session.query(UserPrivate).filter_by(user=user).first()
        if up:
            up.password = password_hash
            up.updated_at = datetime.datetime.now()
        else:
            up = UserPrivate(id=None, user=user, password=password_hash)
        session.add(up)
        return up


class UserView(ServerDBBaseView):
    def __init__(self, db: ServerStorage) -> None:
        super().__init__(db)

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
            stmt = (
                select(User)
                .join(UserStatus, isouter=True)
            )
            users = session.scalars(stmt).fetchall()
            if not users:
                return result
            result = [UserSerializer.from_db(user) for user in users if only_active and user.is_active or not only_active]
        return list(result)

    def get_hash(self, user_name: str, only_active=True) -> Union[str, None]:
        with Session(self.db_engine) as session:
            user = self._user_get(session, user_name)
            if not user:
                return None
            if only_active and not user.is_active:
                return None

            user_id = user.id

            stmt = (
                select(UserPrivate.password)
                .where(UserPrivate.user_id == user_id)
            )
            return session.scalars(stmt).first()

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
                .where(UserContact.user_id == user.id,
                       UserContact.is_active == True,
                       User.is_active == True)
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
                select(UserStatus)
                .join(User, UserStatus.user_id == User.id)
                .where(User.id == user.id,
                       User.is_active == True)
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

    def _user_contact_get(self, session: Session, user: User, contact: User) -> Union[UserContact, None]:
        return session.query(UserContact).filter_by(contact_id=contact.id, user_id=user.id).first()

    def _user_contact_add(self, session: Session, user: User, contact: User) -> UserContact:
        """ Warning! Check user existence before using """
        user_contact = UserContact(id=None, user_id=user.id, contact_id=contact.id)
        session.add(user_contact)
        return user_contact
