from typing import List, Union

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from gb_python_async01.server.core.model import MessageInfo, UserStatistic
from gb_python_async01.server.core.serializers import MessageSerializer
from gb_python_async01.server.db.config import ServerDBBaseView
from gb_python_async01.server.db.errors import ServerDBError
from gb_python_async01.server.db.model import User, Message


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
                sent = sum([line[1] for line in messages_sent if line[1] == user.id])
                received = sum(
                    [line[1] for line in messages_received if line[1] == user.id]
                )
                stat = UserStatistic(user=user.name, sent=sent, received=received)
                result.append(stat)
        return result
