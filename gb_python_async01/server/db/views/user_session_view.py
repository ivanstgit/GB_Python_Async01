import datetime
from typing import List, Optional, Union

from sqlalchemy import select
from sqlalchemy.orm import Session

from gb_python_async01.server.core.model import UserSessionInfo
from gb_python_async01.server.core.serializers import UserSessionSerializer
from gb_python_async01.server.db.config import ServerDBBaseView, ServerStorage
from gb_python_async01.server.db.model import User, UserSession, extpk
from gb_python_async01.server.db.errors import *


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
