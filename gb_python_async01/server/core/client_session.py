from datetime import datetime
from functools import wraps
from queue import Queue
import threading
import time
from typing import List, Optional, Tuple, Union

from gb_python_async01.server.core.errors import ServerNotAuthorized
from gb_python_async01.server.core.serializers import UserSessionSerializer
from gb_python_async01.server.db.message_view import MessageInfo, MessageView
from gb_python_async01.server.db.model import Message as dbMessage
from gb_python_async01.server.db.model import User as dbUser
from gb_python_async01.server.db.model import UserSession as dbUserSession
from gb_python_async01.server.db.user_session_view import UserSessionView
from gb_python_async01.server.db.user_view import ServerStorage, UserView
from gb_python_async01.transport.endpoints import *
from gb_python_async01.transport.errors import JIMSerializerError
from gb_python_async01.transport.model.message import *
from gb_python_async01.transport.protocol import JIMSerializer
from gb_python_async01.transport.serializers.user import JIMUserSerializer
from gb_python_async01.utils.errors import UtilsSecurityAuthError, UtilsTrSecurityError
from gb_python_async01.utils.security import ServerSecurity


class OutMessagesObserver():
    def register_out_message(self, m_out: MessageInfo):
        raise NotImplemented

    def logout(self, user_name):
        raise NotImplemented


class LoginRequired():
    def __call__(self, func):
        @wraps(func)
        def check_is_authenticated(*args, **kwargs):
            cl = args[0]
            if isinstance(cl, ClientSession):
                if cl.is_authenticated:
                    result = func(*args, **kwargs)
                    return result
            raise ServerNotAuthorized
        return check_is_authenticated


class ClientSession():
    """ Connected client, keeps session and message queues and action/response order"""
    _out_messages: List[MessageInfo]
    current_message_to_send: Optional[JIMMessage]
    current_message_sent: Optional[MessageInfo]

    def __init__(self, logger, db: ServerStorage, host: str, port: int, out_observer: OutMessagesObserver) -> None:
        self._logger = logger
        self._db = db
        self._host = host
        self._port = port
        self._out_observer = out_observer

        self.JIM = JIMSerializer()

        # Server response on accepted message - client waiting
        self.current_message_to_send = None
        # Last message sent to client - response waiting
        self.current_message_sent = None

        # after first message
        self._sec = None

        # after auth
        self._secured = False
        self._username = None
        self._is_authenticated = False
        self._history_processed = False
        self._out_messages = []

        self._db_user_view = UserView(db)
        self._db_user_session_view = UserSessionView(db)
        self._db_message_view = MessageView(db)
        self._db_session_id = None

    @property
    def is_authenticated(self) -> bool:
        return self._is_authenticated

    @property
    def username(self) -> Optional[str]:
        return self._username

    def process_inbound_message(self, msgb: bytes):
        """ get message, save response in self"""

        try:
            if self._sec and self._sec.check_if_encrypted(msgb):
                msgb = self._sec.decrypt_message(msgb)
            msg = self.JIM.from_bytes(msgb)
        except UtilsTrSecurityError:
            self.current_message_to_send = JIMResponse400('Decryption error')
            return
        except (JIMSerializerError, JIMValidationError):
            self.current_message_to_send = JIMResponse400('Serialization error')
            return

        if isinstance(msg, JIMAuth):
            self.current_message_to_send = self._auth(msg)
        elif isinstance(msg, JIMAction):
            try:
                response = self._action(msg)
            except ServerNotAuthorized:
                response = JIMResponse401()
            self.current_message_to_send = response
        elif isinstance(msg, JIMResponse):
            if self.current_message_sent:
                self._response_on_out_message(self.current_message_sent, msg)
                self.current_message_sent = None
        else:
            self.current_message_to_send = JIMResponse400()

    def register_out_message(self, msg: MessageInfo):
        """ message from another client """
        self._out_messages.append(msg)

    def get_next_out_message(self) -> Optional[bytes]:
        """
        response - first priority
        callback would be better, but...
        """
        resp = self.current_message_to_send
        if resp:
            self.current_message_to_send = None
            msg = resp
            if self.is_authenticated and not self._history_processed:
                self._fill_out_messages_from_db()
                self._history_processed = True
        elif len(self._out_messages) > 0:

            self.current_message_sent = self._out_messages.pop()
            msg = self.current_message_sent.action
        else:
            return None

        try:
            msgb = self.JIM.to_bytes(msg)
            if self._sec and self._secured:
                msgb = self._sec.encrypt_message(msgb)
            return msgb
        except (JIMSerializerError, JIMValidationError):
            self._logger.error(f'Serialization error while sending message {msg} to {self.username}')
        except UtilsTrSecurityError:
            self._logger.error(f'Encryption error while sending message {msg} to {self.username}')
        return None

    def close(self):
        self._logout()

    def __str__(self) -> str:
        return f'ClientSession of {self.username}'

    def _auth(self, msg: JIMAuth) -> JIMResponse:
        # Повторный запрос на аутентификацию с того же сокета - (?)
        if self.is_authenticated == True:
            self._logout()

        if msg.auth_action == JIMAuth.step1:
            # public client key -> session key
            if msg.data1 and msg.data1 != '':
                self._pubkey = msg.data1
                self._sec = ServerSecurity(self._pubkey)
                self._secured = False
                step2 = self._sec.process_auth_step2()
                return JIMResponse202(data=step2)

        elif msg.auth_action == JIMAuth.step2:
            # auth check
            if self._sec and msg.data1 and msg.data1 != '' and msg.data2 and msg.data2 != '':
                self._secured = True
                try:
                    login = msg.data1
                    db_user = self._db_user_view.get(login)
                    if not db_user:
                        return JIMResponse402()

                    password = self._db_user_view.get_hash(login)
                    if password and password != '':
                        self._sec.process_auth_step4(msg.data2, password)
                    else:
                        return JIMResponse402()

                    last_login = self._db_user_session_view.get_last(login)

                    if last_login and last_login.is_active:
                        return JIMResponse409()

                    try:
                        self._db_session_id = self._db_user_session_view.login(user_name=login, ip=self._host, port=self._port, pubkey=self._pubkey)

                    except Exception:
                        return JIMResponse500()
                    else:
                        self._username = login
                        self._user = db_user
                        self._is_authenticated = True
                    return JIMResponse200()
                except UtilsSecurityAuthError:
                    return JIMResponse402()

        return JIMResponse400()

    def _logout(self):
        if self._username:
            self._db_user_session_view.logout(self._username)
        self._is_authenticated = False

    @LoginRequired()
    def _action(self, action: JIMAction) -> JIMResponse:
        try:
            if isinstance(action, JIMActionPresence):
                self._db_user_view.status_update(action.user_account, action.user_status)  # type: ignore
                return JIMResponse200()

            elif isinstance(action, JIMActionMessage):
                receiver = action.receiver
                sender = action.sender
                if sender and sender == self._username and receiver and self._db_user_view.get(receiver) and self._db_session_id:
                    out = self._db_message_view.add(MessageInfo(None, action, self._db_session_id))
                    self._out_observer.register_out_message(out)
                    return JIMResponse202(data=[out.msg_id])
                return JIMResponse404()

            elif isinstance(action, JIMActionGetContacts):
                res = []
                contacts = self._db_user_view.contact_get_list(user_name=action.user_account)  # type: ignore
                if contacts:
                    for contact in contacts:
                        si = self._db_user_session_view.get_last(contact.user)
                        if si:  # If contact never connected -> it's not what we are looking for
                            jimuser = UserSessionSerializer.to_transport(contact, si)
                            res.append(JIMUserSerializer.to_dict(jimuser))
                if len(res) == 0:
                    res = None
                return JIMResponse202Contacts(res)

            elif isinstance(action, JIMActionAddContact):
                contact = action.contact
                if self._username == contact:
                    return JIMResponse400(error="Can't add yourself as a contact")

                if contact and self._db_user_view.get(contact):
                    us = self._db_user_view.contact_add(user_name=self._username, contact_name=contact)  # type: ignore
                    si = self._db_user_session_view.get_last(contact)
                    if si:  # If contact never connected -> it's not what we are looking for
                        res = [JIMUserSerializer.to_dict(UserSessionSerializer.to_transport(us, si))]
                    else:
                        res = None
                    return JIMResponse202Contacts(res)
                return JIMResponse404()

            elif isinstance(action, JIMActionDeleteContact):
                contact = action.contact
                if self._username == contact:
                    return JIMResponse400(error="Can't add/delete yourself as a contact")

                if contact and self._db_user_view.get(contact):
                    self._db_user_view.contact_delete(user_name=self._username, contact_name=contact)  # type: ignore
                    return JIMResponse200()
                return JIMResponse404()

            elif isinstance(action, JIMActionExit):
                self._logout()
                self._out_observer.logout(self.username)
                return JIMResponse200()

            return JIMResponse400()

        except Exception as e:
            return JIMResponse500()

    def _fill_out_messages_from_db(self):
        if self.username:
            try:
                pass
                # self._out_messages = self._db_message_view.get_undelivered_list(self.username)
            except Exception as e:
                self._logger.error(f'Error on selecting undelivered messages for {self}')

    def _response_on_out_message(self, msg: MessageInfo, response: JIMResponse):
        if isinstance(msg.action, JIMActionMessage) and not response.is_error:
            self._db_message_view.set_delivered(msg)
            # action to sender (?)
