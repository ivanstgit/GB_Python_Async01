
from typing import Optional
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from gb_python_async01.client.db.model import *
from gb_python_async01.client.errors import ClientDBError
from gb_python_async01.transport.model.user import JIMUser


class ClientStorage():
    def __init__(self, db_url) -> None:
        self.db_engine = create_engine(db_url, echo=False, pool_recycle=7200)

    def init_db_tables(self):
        Base.metadata.create_all(self.db_engine)

    def contact_update_from_server(self, c: JIMUser) -> Contact:
        return self.contact_add_or_update(
            contact_name=c.username,
            last_login=datetime.datetime.fromtimestamp(c.last_login),
            status=c.status or '',
            pubkey=c.pubkey or ''
        )

    def contact_add_or_update(self, contact_name: str, last_login: datetime.datetime, status: str, pubkey: str) -> Contact:
        with Session(self.db_engine) as session:
            contact = session.query(Contact).filter_by(name=contact_name).first()
            if not contact:
                contact = Contact(name=contact_name)
            contact.is_active = True
            contact.last_login = last_login
            contact.status = status
            contact.pubkey = pubkey
            session.add(contact)
            session.commit()
            return contact

    def contact_delete(self, contact_name: str):
        with Session(self.db_engine) as session:
            contact = session.query(Contact).filter_by(name=contact_name).first()
            if contact:
                contact.is_active = False
                session.add(contact)
            session.commit()

    def contact_get(self, contact_name: str, only_active=True) -> Optional[Contact]:
        with Session(self.db_engine) as session:
            if only_active:
                contact = session.query(Contact).filter_by(name=contact_name, is_active=True).first()
            else:
                contact = session.query(Contact).filter_by(name=contact_name).first()
            return contact

    def contact_list(self) -> List[Contact]:
        with Session(self.db_engine) as session:
            stmt_contacts = (
                select(Contact)
                .where(Contact.is_active == True)
            )
            contacts = session.scalars(stmt_contacts).fetchall()
            if not contacts:
                contacts = []
            return list(contacts)

    def message_add(self, contact_name: str, is_inbound: bool, created_at: datetime.datetime, msg_txt: str):
        with Session(self.db_engine) as session:
            contact = session.query(Contact).filter_by(name=contact_name).first()
            if not contact:
                contact = Contact(name=contact_name, is_active=False)
                session.add(contact)
                session.commit()

            message = MessageHistory(id=None,
                                     contact_id=contact.id,
                                     created_at=created_at,
                                     is_inbound=is_inbound,
                                     msg_txt=msg_txt)
            session.add(message)
            session.commit()

    def message_history(self, contact_name: str, limit: int) -> list:
        with Session(self.db_engine) as session:
            contact = session.query(Contact).filter_by(name=contact_name).first()
            if contact:
                stmt_message_history = (
                    select(MessageHistory)
                    .where(MessageHistory.contact_id == contact.id)
                    .order_by(-MessageHistory.created_at)
                    .limit(limit)
                )
                message_history = session.scalars(stmt_message_history).fetchall()
                return list(message_history)
            else:
                return []

# raise ClientDBError(msg=f'Incorrect contact {contact_name}')
