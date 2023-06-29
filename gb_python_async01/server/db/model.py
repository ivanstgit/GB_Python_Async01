# Server DB model
import datetime
from typing import Annotated, List, Optional

from sqlalchemy import FetchedValue, ForeignKey, Integer, String, UnicodeText, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

intpk = Annotated[int, mapped_column('id', Integer, primary_key=True, autoincrement=True)]
extpk = int
db_time = datetime.datetime
created_at = Annotated[
    datetime.datetime,
    mapped_column(nullable=False, insert_default=datetime.datetime.now()),
]
updated_at = Annotated[
    datetime.datetime,
    mapped_column(nullable=False, insert_default=datetime.datetime.now(), onupdate=datetime.datetime.now()),
]


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[intpk]
    name: Mapped[str] = mapped_column('name', String(30), unique=True)

    status: Mapped['UserStatus'] = relationship(back_populates="user")
    login_history: Mapped[List['UserLoginHistory']] = relationship(back_populates="user")

    def __repr__(self) -> str:
        return f'User(id={self.id!r}, name={self.name!r}'


class UserLoginHistory(Base):
    __tablename__ = "user_login_history"

    id: Mapped[intpk]
    user_id: Mapped[extpk] = mapped_column('user_id', ForeignKey('users.id'))
    login_at: Mapped[created_at]
    ip: Mapped[str] = mapped_column('ip')
    port: Mapped[int] = mapped_column('port')
    is_active: Mapped[bool] = mapped_column('is_active')
    updated_at: Mapped[updated_at]

    user: Mapped["User"] = relationship(back_populates="login_history")


class UserStatus(Base):
    __tablename__ = "user_status"

    id: Mapped[intpk]
    user_id: Mapped[extpk] = mapped_column('user_id', ForeignKey('users.id'))
    updated_at: Mapped[updated_at]
    status: Mapped[str] = mapped_column('status', String(30))

    user: Mapped["User"] = relationship(back_populates="status")


class UserContact(Base):
    __tablename__ = "user_contacts"

    id: Mapped[intpk]
    user_id: Mapped[extpk] = mapped_column('user_id', ForeignKey('users.id'))
    contact_id: Mapped[extpk] = mapped_column('contact_id', ForeignKey('users.id'))
    created_at: Mapped[created_at]
    is_active: Mapped[bool] = mapped_column('is_active', default=True)

    # user: Mapped["User"] = relationship(back_populates="users")
    # contact: Mapped["User"] = relationship(back_populates="contacts")


class MessageHistory(Base):
    __tablename__ = "message_history"

    id: Mapped[intpk]
    sender_id: Mapped[extpk] = mapped_column('sender_id', ForeignKey('users.id'))
    receiver_id: Mapped[extpk] = mapped_column('receiver_id', ForeignKey('users.id'))
    created_at: Mapped[created_at]
    msg_txt: Mapped[str] = mapped_column('msg_txt', UnicodeText)
    is_delivered: Mapped[bool] = mapped_column('is_delivered', default=False)

    # sender: Mapped["User"] = relationship()
