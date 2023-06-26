
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from gb_python_async01.server.db.model import *
from gb_python_async01.common.model.user import User as CommonUser


class ServerStorage():
    def __init__(self, db_url) -> None:
        self.db_engine = create_engine(db_url, echo=False, pool_recycle=7200)

    def init_db_tables(self):
        Base.metadata.create_all(self.db_engine)

    def user_login(self, user_name, ip, port, status):
        with Session(self.db_engine) as session:
            user = session.query(User).filter_by(name=user_name).first()
            if not user:
                user = User(id=None, name=user_name)
                session.add(user)
                session.commit()

            login_hist_record = UserLoginHistory(
                user_id=user.id,
                ip=ip,
                port=port)
            session.add(login_hist_record)

            user_status = session.query(UserStatus).filter_by(user_id=user.id).first()
            if not user_status:
                user_status = UserStatus(
                    user_id=user.id,
                    status=status
                )
            user_status.is_active = True
            user_status.updated_at = datetime.datetime.now()
            session.add(user_status)

            session.commit()

    def user_logout(self, user_name):
        with Session(self.db_engine) as session:
            user = session.query(User).filter_by(name=user_name).first()
            if user:
                user_status = session.query(UserStatus).filter_by(user_id=user.id).first()
                if user_status:
                    user_status.is_active = False
                    user_status.updated_at = datetime.datetime.now()
                    session.add(user_status)
                    session.commit()

    def user_get_list(self, user_names: list) -> list:
        result = []
        with Session(self.db_engine) as session:
            stmt_users = (
                select(User)
                .join(UserStatus, isouter=True)
                .where(User.name.in_(user_names))
            )
            stmt_last_login = (
                select(User.id, func.max(UserLoginHistory.login_at))
                .join(User)
                .where(User.name.in_(user_names))
                .group_by(User.id)
                .order_by(User.id, UserLoginHistory.login_at)
            )
            users_history = session.execute(stmt_last_login).fetchall()
            users = session.scalars(stmt_users).fetchall()

            for user in users:
                last_login = max([hist_line[1] for hist_line in users_history if hist_line[0] == user.id], default=None)
                common_user = CommonUser(username=user.name, status=user.status.status, is_active=user.status.is_active, last_login=last_login)
                result.append(common_user)
        return result
        # users = session.query(User).filter_by(name=user_name).first()
        # if user:

    def user_get(self, user_name: str):
        res = self.user_get_list([user_name])
        if len(res):
            return res.pop()
        return None
