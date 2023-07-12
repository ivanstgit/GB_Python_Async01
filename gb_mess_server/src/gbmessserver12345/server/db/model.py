"""Модель БД"""
import datetime
from typing import Annotated, List

from sqlalchemy import (
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.sql import default_comparator
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

intpk = Annotated[
    int, mapped_column("id", Integer, primary_key=True, autoincrement=True)
]
extpk = int
db_time = datetime.datetime
created_at = Annotated[
    datetime.datetime,
    mapped_column(nullable=False, insert_default=datetime.datetime.now()),
]
updated_at = Annotated[
    datetime.datetime,
    mapped_column(
        nullable=False,
        insert_default=datetime.datetime.now(),
        onupdate=datetime.datetime.now(),
    ),
]


class Base(DeclarativeBase):
    pass


class User(Base):
    """
    Пользователи

    Для обеспечения ссылочной целостности пользователи не удаляются из БД, только деактивируются
    """

    __tablename__ = "users"

    id: Mapped[intpk]
    name: Mapped[str] = mapped_column("name", String(30), unique=True)
    is_active: Mapped[bool] = mapped_column("is_active", default=True)
    updated_at: Mapped[updated_at]

    status: Mapped["UserStatus"] = relationship(back_populates="user")
    login_history: Mapped[List["UserSession"]] = relationship(back_populates="user")

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, name={self.name!r}"

    def activate(self):
        self.is_active = True

    def deactivate(self):
        self.is_active = False


class UserPrivate(Base):
    """Закрытые данные пользователей"""

    __tablename__ = "user_private"

    id: Mapped[intpk]
    user_id: Mapped[extpk] = mapped_column("user_id", ForeignKey("users.id"))
    updated_at: Mapped[updated_at]
    password: Mapped[str] = mapped_column("password", String(128))

    user: Mapped["User"] = relationship()

    def __repr__(self) -> str:
        return f"UserPrivate(id={self.id!r}"


class UserSession(Base):
    """
    История регистраций пользователя

    Публичный ключ хранится для отправки пользователю-контакту
    Для отложенной отправки важно передать контакту тот ключ, которым сообщение было зашифровано!
    """

    __tablename__ = "user_sessions"

    id: Mapped[intpk]
    user_id: Mapped[extpk] = mapped_column("user_id", ForeignKey("users.id"))
    created_at: Mapped[created_at]
    ip: Mapped[str] = mapped_column("ip")
    port: Mapped[int] = mapped_column("port")
    is_active: Mapped[bool] = mapped_column("is_active")
    is_last: Mapped[bool] = mapped_column("is_last")  # SQL query optimization
    updated_at: Mapped[updated_at]
    pubkey: Mapped[str]

    user: Mapped["User"] = relationship()

    def activate(self):
        self.is_active = True

    def deactivate(self):
        self.is_active = False


class UserStatus(Base):
    """Публичные данные пользователей"""

    __tablename__ = "user_status"

    id: Mapped[intpk]
    user_id: Mapped[extpk] = mapped_column("user_id", ForeignKey("users.id"))
    updated_at: Mapped[updated_at]
    status: Mapped[str] = mapped_column("status", String(30))

    user: Mapped["User"] = relationship(back_populates="status", viewonly=True)


class UserContact(Base):
    """
    Контакты пользователей

    Для обеспечения ссылочной целостности контакты не удаляются из БД, только деактивируются
    """

    __tablename__ = "user_contacts"

    id: Mapped[intpk]
    user_id: Mapped[extpk] = mapped_column("user_id", ForeignKey("users.id"))
    contact_id: Mapped[extpk] = mapped_column("contact_id", ForeignKey("users.id"))
    created_at: Mapped[created_at]
    is_active: Mapped[bool] = mapped_column("is_active", default=True)

    user: Mapped["User"] = relationship(foreign_keys=[user_id], viewonly=True)
    contact: Mapped["User"] = relationship(foreign_keys=[contact_id], viewonly=True)

    def activate(self):
        """Добавить контакт"""
        self.is_active = True

    def deactivate(self):
        """Удалить контакт"""
        self.is_active = False


class Message(Base):
    """
    История сообщений

    Контент сообщения зашифрован ключем отправителя, действующим
    на момент регистрации, поэтому храним ссылку на него.
    Контент сообщения очищается после получения адресатом
    """

    __tablename__ = "messages"

    id: Mapped[intpk]
    sender_id: Mapped[extpk] = mapped_column("sender_id", ForeignKey("users.id"))
    receiver_id: Mapped[extpk] = mapped_column("receiver_id", ForeignKey("users.id"))
    created_at: Mapped[db_time]
    msg_txt: Mapped[str] = mapped_column("msg_txt", Text)
    is_delivered: Mapped[bool] = mapped_column("is_delivered", default=False)
    sender_session_id: Mapped[extpk] = mapped_column(
        "login_id", ForeignKey("user_sessions.id")
    )

    sender: Mapped["User"] = relationship(foreign_keys=[sender_id], viewonly=True)
    receiver: Mapped["User"] = relationship(foreign_keys=[receiver_id], viewonly=True)

    def set_delivered(self) -> None:
        self.is_delivered = True
        self.msg_txt = ""
