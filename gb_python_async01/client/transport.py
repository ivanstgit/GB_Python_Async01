# Модуль отвечает за техническое обеспечение обмена сообщениями с сервером
# Авторизация, сериализация сообщений в объектную модель
import os
from typing import Union
from gb_python_async01.client.config import ClientConfig
from gb_python_async01.client.errors import ClientNoConnectionError
from gb_python_async01.transport.errors import *
from gb_python_async01.transport.model.message import *
from gb_python_async01.transport.endpoints import ClientEndpoint
from gb_python_async01.transport.protocol import JIMSerializer
from gb_python_async01.utils.errors import UtilsSecurityValidationError
from gb_python_async01.utils.security import ClientSecurity


class ClientTransport():
    def __init__(self, config: ClientConfig):
        self.config = config

        self.serializer = JIMSerializer()
        self.lock = None
        self.waiting_time = 0.1

        self.srv_host = config.srv_host
        self.srv_port = config.srv_port

        self._conn = None
        self._user_name = None
        self._sec = None

    @property
    def is_connected(self):
        return self._conn and self._conn.is_connected

    @property
    def user(self):
        return self._user_name

    def connect(self, logger) -> Optional[str]:
        try:
            # Connecting to server
            logger.info(f'Connecting to {self.srv_host}:{self.srv_port}')
            if self._conn:
                self._conn.close()

            self._conn = ClientEndpoint(message_max_size=self.config.message_max_size)
            # Reading and writing in one socket -> timeout needed for resource lock releasing
            self._conn.connect_to_server(host=self.srv_host, port=self.srv_port, timeout=1)

        except (EndpointCommunicationError, Exception) as e:
            if self._conn:
                self._conn.close()
            logger.critical(e)
            return f'Ошибка при подключении к серверу: {e}'

        return None

    def login(self, logger, user_name: str, password: str) -> Optional[str]:
        try:
            if not self._conn:
                return f'Отсутствует подключение к серверу'

            # step 1: public key send
            key_file_name = os.path.join(self.config.var_dir, 'key', f'{user_name}.key')
            try:
                self._sec = ClientSecurity(key_file_name, 'evjwoi[verkfpo3]')
                step1 = self._sec.process_auth_step1()
            except Exception as e:
                return f'Ошибка при авторизации, 1 шаг: {e}'
            msg = JIMAuth(JIMAuth.step1, step1, '')
            self._conn.put_message(self.serializer.to_bytes(msg))

            response = self.serializer.decode_response(self._conn.get_message())
            if response.is_error or not response.data or not isinstance(response.data, str):
                return f'Ошибка при авторизации, 1 шаг - сервер: {response.error}'

            step2 = response.data
            try:
                step3 = self._sec.process_auth_step3(step2, user_name, password)
            except Exception as e:
                return f'Ошибка при авторизации, 2 шаг: {e}'
            msg = JIMAuth(JIMAuth.step2, user_name, step3)
            response = self.send_action(logger, msg)
            if response.is_error:
                return f'Ошибка при авторизации, 2 шаг - сервер: {response.error}'

            self._user_name = user_name

        except (EndpointCommunicationError, Exception) as e:
            if self._conn:
                self._conn.close()
            logger.critical(e)
            return f'Ошибка при проверке логина/пароля: {e}'

        return None

    def send_action(self, logger, msg: Union[JIMAction, JIMAuth]) -> JIMResponse:
        try:
            logger.debug(f'Sending {msg}')
            self._send_message_enc(self.serializer.to_bytes(msg))
            response = self.serializer.decode_response(self._read_message_enc())
            logger.debug(f'Response {response}')
            if response.is_error:
                if isinstance(msg, JIMAction):
                    action = msg.action
                else:
                    action = ''
                logger.debug(f'Error response on {msg.type} {action} message: {response}')
            return response
        except EndpointCommunicationError as e:
            if self._conn:
                self._conn.close()
            raise e

    def read_action(self, logger) -> JIMAction:
        try:
            action = self.serializer.decode_action(self._read_message_enc())
            logger.debug(f'Accepting {action}')
            self._send_message_enc(self.serializer.encode_response(JIMResponse200()))
            return action
        except EndpointCommunicationError as e:
            if self._conn:
                self._conn.close()
            raise e

    @property
    def sec(self):
        return self._sec

    def _send_message_enc(self, msg: bytes):
        if not self._conn:
            raise ClientNoConnectionError
        if not self._sec:
            raise UtilsSecurityValidationError
        msgb = self._sec.encrypt_message(msg)
        self._conn.put_message(msgb)

    def _read_message_enc(self) -> bytes:
        if not self._conn:
            raise ClientNoConnectionError
        if not self._sec:
            raise UtilsSecurityValidationError

        msgb = self._conn.get_message()
        if self._sec.check_if_encrypted(msgb):
            msgb = self._sec.decrypt_message(msgb)
        return msgb
