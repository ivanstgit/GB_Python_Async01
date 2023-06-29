
import time
from sqlalchemy import create_engine, select, update
from sqlalchemy.orm import Session

from gb_python_async01.server.db.model import *
from gb_python_async01.server.errors import ServerDBError
# from gb_python_async01.transport.model.user import User as CommonUser


class ActiveUser():
    def __init__(self, user: str, connected_at: datetime.datetime, ip_addr: str, ip_port: int) -> None:
        self.user = user
        self.connected_at = connected_at
        self.ip_addr = ip_addr
        self.ip_port = ip_port


class UserStatistic():
    def __init__(self, user: str, sent: int, received: int) -> None:
        self.user = user
        self.sent = sent
        self.received = received


class ServerStorage():
    def __init__(self, db_url) -> None:
        self.db_engine = create_engine(db_url, echo=False, pool_recycle=7200)

    def init_db_tables(self):
        Base.metadata.create_all(self.db_engine)

    def clear_active_connections(self):
        with Session(self.db_engine) as session:
            stmt_users_active_logins = (
                select(UserLoginHistory)
                .where(UserLoginHistory.is_active == True)
                .group_by(UserLoginHistory.user_id)
            )
            users_active_logins = session.scalars(stmt_users_active_logins).fetchall()

            for loginh in users_active_logins:
                loginh.is_active = False
                session.add(loginh)
            session.commit()

    # internal use methods (db_model format)
    def user_get(self, user_name: str):
        with Session(self.db_engine) as session:
            return session.query(User).filter_by(name=user_name).first()

    def user_add(self, user_name: str):
        with Session(self.db_engine) as session:
            user = session.query(User).filter_by(name=user_name).first()
            if not user:
                user = User(id=None, name=user_name)
                session.add(user)
                session.commit()
            return user

    def user_contact_get(self, user: User, contact: User) -> UserContact:
        with Session(self.db_engine) as session:
            user_contact = session.query(UserContact).filter_by(contact_id=contact.id, user_id=user.id, is_active=True).first()
            if user_contact:
                user_contact.is_active = True
            else:
                user_contact = UserContact(id=None, user_id=user.id, contact_id=contact.id)
            session.add(user_contact)
            session.commit()
            return user_contact

    def user_contact_add(self, user: User, contact: User) -> UserContact:
        with Session(self.db_engine) as session:
            user_contact = session.query(UserContact).filter_by(contact_id=contact.id, user_id=user.id).first()
            if user_contact:
                user_contact.is_active = True
            else:
                user_contact = UserContact(id=None, user_id=user.id, contact_id=contact.id)
            session.add(user_contact)
            session.commit()
            return user_contact

    def user_contact_delete(self, user_contact: UserContact) -> None:
        with Session(self.db_engine) as session:
            user_contact.is_active = False
            session.add(user_contact)
            session.commit()

    # client integration (integration model format)

    def cl_user_login(self, user_name, ip, port, status):
        user = self.user_get(user_name)
        if not user:
            user = self.user_add(user_name)

        with Session(self.db_engine) as session:
            login_hist_record = UserLoginHistory(
                user_id=user.id,
                ip=ip,
                port=port,
                is_active=True)
            session.add(login_hist_record)

            user_status = session.query(UserStatus).filter_by(user_id=user.id).first()
            if not user_status:
                user_status = UserStatus(
                    user_id=user.id,
                    status=status
                )
            user_status.updated_at = datetime.datetime.now()
            session.add(user_status)

            session.commit()

    def cl_user_logout(self, user_name):
        user = self.user_get(user_name)
        if user:
            with Session(self.db_engine) as session:
                user_login_history = session.query(UserLoginHistory).filter_by(user_id=user.id, is_active=True).first()
                if user_login_history:
                    user_login_history.is_active = False
                    user_login_history.updated_at = datetime.datetime.now()
                    session.add(user_login_history)
                    session.commit()
        else:
            raise ServerDBError('User not found')

    def cl_user_contact_add(self, user_name, contact_name):
        user = self.user_get(user_name)
        contact = self.user_get(contact_name)
        if user and contact:
            self.user_contact_add(user, contact)
        else:
            raise ServerDBError('User or contact not found')

    def cl_user_contact_delete(self, user_name, contact_name):
        user = self.user_get(user_name)
        contact = self.user_get(contact_name)
        if user and contact:
            user_contact = self.user_contact_get(user, contact)
            if user_contact:
                self.user_contact_delete(user_contact)
        else:
            raise ServerDBError('User or contact not found')

    def cl_user_contact_get_list(self, user_name: str) -> list:
        result = []
        with Session(self.db_engine) as session:
            user = session.query(User).filter_by(name=user_name).first()
            if user:
                stmt_contacts = (
                    select(User.name)
                    .join(UserContact, UserContact.contact_id == User.id)
                    .where(UserContact.user_id == user.id, UserContact.is_active == True)
                )
                contacts = session.scalars(stmt_contacts).fetchall()
                result = list(contacts)
        return result

    def cl_message_add(self, sender_name, receiver_name, dt_time: datetime.datetime, msg_txt: str) -> extpk:
        with Session(self.db_engine) as session:
            sender = session.query(User).filter_by(name=sender_name).first()
            receiver = session.query(User).filter_by(name=receiver_name).first()
            if sender and receiver:
                message = MessageHistory(id=None, sender_id=sender.id, receiver_id=receiver.id, created_at=dt_time, msg_txt=msg_txt)
                session.add(message)
                session.commit()
                return message.id
            raise ServerDBError('Sender or receiver not found')

    def cl_message_mark_delivered(self, message_id: extpk) -> None:
        with Session(self.db_engine) as session:
            message = session.query(MessageHistory).filter_by(id=message_id).first()
            if message:
                message.is_delivered = True
                session.add(message)
                session.commit()
            else:
                raise ServerDBError('Message not found')

    # gui integration (gui model format)
    def gui_get_active_user_list(self) -> list:
        result = []
        with Session(self.db_engine) as session:
            stmt_users_active_logins = (
                select(UserLoginHistory)
                .join(User)
                .where(UserLoginHistory.is_active == True)
                .group_by(UserLoginHistory.user_id)
            )
            users_active_logins = session.scalars(stmt_users_active_logins).fetchall()

            for loginh in users_active_logins:
                active_user = ActiveUser(user=loginh.user.name,
                                         connected_at=loginh.login_at,
                                         ip_addr=loginh.ip,
                                         ip_port=loginh.port)
                result.append(active_user)
        return result

    def gui_user_get_statistics(self) -> list:
        result = []
        with Session(self.db_engine) as session:
            stmt_users = (
                select(User)
            )
            stmt_mesg_sent = (
                select(MessageHistory.sender_id, func.count(MessageHistory.id))
                .group_by(MessageHistory.sender_id)
            )
            stmt_mesg_received = (
                select(MessageHistory.receiver_id, func.count(MessageHistory.id))
                .group_by(MessageHistory.receiver_id)
            )
            users = session.scalars(stmt_users).fetchall()
            messages_sent = session.execute(stmt_mesg_sent).fetchall()
            messages_received = session.execute(stmt_mesg_received).fetchall()

            for user in users:
                sent = sum([line[1] for line in messages_sent if line[1] == user.id])
                received = sum([line[1] for line in messages_received if line[1] == user.id])
                stat = UserStatistic(user=user.name, sent=sent, received=received)
                result.append(stat)
        return result
