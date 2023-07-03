
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from gb_python_async01.client.db.model import *
from gb_python_async01.client.errors import ClientDBError
from gb_python_async01.transport.model.user import User as CommonUser


class ClientStorage():
    def __init__(self, db_url) -> None:
        self.db_engine = create_engine(db_url, echo=False, pool_recycle=7200)

    def init_db_tables(self):
        Base.metadata.create_all(self.db_engine)

    # def contacts_update_all(self, contact_name_list: list):
    #     with Session(self.db_engine) as session:
    #         stmt_contacts = (
    #             select(Contact)
    #         )
    #         contacts = session.scalars(stmt_contacts).fetchall()
    #         contact_names = list([contact.name for contact in contacts])

    #         to_delete = [contact for contact in contacts if contact.name not in contact_name_list]

    #         for contact in to_delete:
    #             contact.is_active = False
    #             session.add(contact)

    #         to_add = [Contact(name=contact_name, is_active=True)
    #                   for contact_name in contact_name_list if contact_name not in contact_names]
    #         session.add_all(to_add)

    #         session.commit()

    def contact_add(self, contact_name: str) -> Contact:
        with Session(self.db_engine) as session:
            contact = session.query(Contact).filter_by(name=contact_name).first()
            if contact:
                contact.is_active = True
            else:
                contact = Contact(name=contact_name, is_active=True)
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

    def contact_get(self, contact_name: str, only_active=True):
        with Session(self.db_engine) as session:
            if only_active:
                contact = session.query(Contact).filter_by(name=contact_name, is_active=True).first()
            else:
                contact = session.query(Contact).filter_by(name=contact_name).first()
            return contact

    def contact_list(self) -> list:
        with Session(self.db_engine) as session:
            stmt_contacts = (
                select(Contact)
                .where(Contact.is_active == True)
            )
            contacts = session.scalars(stmt_contacts).fetchall()
            if contacts:
                contact_names = list([contact.name for contact in contacts])
            else:
                contact_names = []
            return contact_names

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
