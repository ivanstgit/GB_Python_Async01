# Client DB model
import datetime
from typing import Annotated, List
from sqlalchemy import ForeignKey, String, Integer, UnicodeText
from sqlalchemy.orm import DeclarativeBase, Mapped
from sqlalchemy.orm import mapped_column, relationship

intpk = Annotated[int, mapped_column('id', Integer, primary_key=True, autoincrement=True)]
extpk = int
created_at = Annotated[
    datetime.datetime,
    mapped_column(nullable=False, insert_default=datetime.datetime.now()),
]
updated_at = Annotated[
    datetime.datetime,
    mapped_column(nullable=False, onupdate=datetime.datetime.now()),
]


class Base(DeclarativeBase):
    pass


class Contact(Base):
    __tablename__ = "contacts"

    id: Mapped[intpk]
    name: Mapped[str] = mapped_column('name', String(30), unique=True)
    is_active: Mapped[bool] = mapped_column('is_active')

    message_history: Mapped[List['MessageHistory']] = relationship(back_populates="contact")

    def __repr__(self) -> str:
        return f'User(id={self.id!r}, name={self.name!r}'


class MessageHistory(Base):
    __tablename__ = "message_history"

    id: Mapped[intpk]
    contact_id: Mapped[extpk] = mapped_column('contact_id', ForeignKey('contacts.id'))
    created_at: Mapped[created_at]
    is_inbound: Mapped[bool] = mapped_column('is_inbound')
    msg_txt: Mapped[str] = mapped_column('msg_txt', UnicodeText)

    contact: Mapped["Contact"] = relationship(back_populates="message_history")

    def __repr__(self) -> str:
        if self.is_inbound:
            res = f'Получено {self.created_at}:\n {self.msg_txt}'
        else:
            res = f'Отправлено {self.created_at}:\n {self.msg_txt}'
        return res
