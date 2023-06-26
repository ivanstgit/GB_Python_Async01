# Server DB model
import datetime
from typing import Annotated, List
from typing import Optional
from sqlalchemy import FetchedValue, ForeignKey, func
from sqlalchemy import String, Integer
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

intpk = Annotated[int, mapped_column('id', Integer, primary_key=True, autoincrement=True)]
extpk = int
created_at = Annotated[
    datetime.datetime,
    mapped_column(nullable=False, insert_default=datetime.datetime.now()),
]
updated_at = Annotated[
    datetime.datetime,
    mapped_column(nullable=False, default=datetime.datetime.now()),
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

    user: Mapped["User"] = relationship(back_populates="login_history")


class UserStatus(Base):
    __tablename__ = "user_status"

    id: Mapped[intpk]
    user_id: Mapped[extpk] = mapped_column('user_id', ForeignKey('users.id'))
    updated_at: Mapped[updated_at]
    is_active: Mapped[bool] = mapped_column('is_active')
    status: Mapped[str] = mapped_column('status', String(30))

    user: Mapped["User"] = relationship(back_populates="status")


class UserContacts(Base):
    __tablename__ = "user_contacts"

    id: Mapped[intpk]
    user_id: Mapped[extpk] = mapped_column('user_id', ForeignKey('users.id'))
    contact_id: Mapped[extpk] = mapped_column('contact_id', ForeignKey('users.id'))
    created_at: Mapped[created_at]
    is_active: Mapped[bool] = mapped_column('is_active', default=True)

    # user: Mapped["User"] = relationship(back_populates="users")
    # contact: Mapped["User"] = relationship(back_populates="contacts")
