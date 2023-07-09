# Keeps & manages client sessions and interactions between them (Model/Mapper)
from logging import Logger
from typing import Dict, List, Optional, Tuple
from gb_python_async01.server.core.client_session import ClientSession, OutMessagesObserver
from gb_python_async01.server.db.config import ServerStorage
from gb_python_async01.server.db.user_session_view import UserSessionView
from gb_python_async01.transport.endpoints import Endpoint
from gb_python_async01.transport.model.message import *
from gb_python_async01.server.db.message_view import MessageInfo


class ClientSessionManager(OutMessagesObserver):
    client_sessions: Dict[Endpoint, ClientSession]

    def __init__(self, logger: Logger, db: ServerStorage) -> None:
        self.client_sessions = dict()
        self.logger = logger
        self.db = db

        session_view = UserSessionView(self.db)
        session_view.clear_active_connections()

    def _get_endpoint_from_username(self, user_name: str) -> Optional[Endpoint]:
        if not self.client_sessions:
            return None
        ep = [ep for ep, sess in self.client_sessions.items() if sess.is_authenticated and sess.username == user_name]
        if ep:
            return ep.pop()
        return None

    def _get_session_from_username(self, user_name: str) -> Optional[ClientSession]:
        ep = self._get_endpoint_from_username(user_name)
        if ep:
            return self.get_client_session(ep)
        return None

    def get_client_session(self, ep: Endpoint) -> Optional[ClientSession]:
        if not self.client_sessions:
            self.logger.debug(f'No session found for {ep}')
            return None
        return self.client_sessions.get(ep)

    def get_client_endpoints(self) -> List[Endpoint]:
        if not self.client_sessions:
            return []
        return list(self.client_sessions.keys())

    def add_client(self, ep: Endpoint):
        self.client_sessions[ep] = ClientSession(self.logger, self.db, ep.address[0], ep.address[1], self)
        self.logger.info(f'Client {ep} connected')

    def remove_client(self, ep: Endpoint):
        sess = self.get_client_session(ep)
        if sess:
            sess.close()

        self.client_sessions.pop(ep, None)
        ep.close()
        self.logger.info(f'Client {ep} disconnected')

    def register_out_message(self, m_out: MessageInfo):
        if m_out.action.receiver:
            sess = self._get_session_from_username(m_out.action.receiver)
            if sess:
                sess.register_out_message(m_out)
