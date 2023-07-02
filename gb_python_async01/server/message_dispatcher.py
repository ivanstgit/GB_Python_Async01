from datetime import datetime
import select
import threading
import time

from gb_python_async01.server.config import ServerConfig
from gb_python_async01.server.db.view import ServerStorage
from gb_python_async01.transport.endpoints import *
from gb_python_async01.transport.errors import (EndpointCommunicationError,
                                                JIMSerializerError,
                                                JIMValidationError)
from gb_python_async01.transport.model.message import *
from gb_python_async01.transport.protocol import JIMSerializer
from gb_python_async01.utils.debug_decorators import Log


class ServerMessageDispatcher():
    # port = EndpointPort()
    # host = EndpointHost()

    def __init__(self, logger, config: ServerConfig, db: ServerStorage):
        self.config = config
        self.logger = logger
        self.db = db
        self.serializer = JIMSerializer()
        self.conn = ServerEndpoint(logger=self.logger, message_max_size=self.config.message_max_size)
        self.messages = {}  # messages received, but not delivered
        self.inputs = []  # resources for read
        self.outputs = []  # resources for write
        self.clients = {}  # parameters for resources (username)

    def _send_message(self, client: Endpoint, msg: Action) -> Response:
        self.logger.debug(f'Sending {msg} to {client}')
        client.put_message(self.serializer.encode_action(msg))
        response = self.serializer.decode_response(client.get_message())
        self.logger.debug(f'Response {response}')
        return response

    def _send_response(self, client: Endpoint, msg: Response):
        self.logger.debug(f'Sending response {msg}')
        client.put_message(self.serializer.encode_response(msg))

    def _read_message(self, client: Endpoint) -> Action:
        action = self.serializer.decode_action(client.get_message())
        self.logger.debug(f'Accepting {action}')
        return action

    def _add_client(self, client: Endpoint):
        self.logger.info(f'Client {client} connected')
        if not client in self.inputs:
            self.inputs.append(client)
        self.clients[client] = None

    def _auth_client(self, client: Endpoint, user_name: str, user_status: str) -> bool:
        if client in self.clients and (not user_name in self.clients.values()):
            self.logger.info(f'Client {client} authorized with name {user_name}')
            self.clients[client] = user_name
            self.db.cl_user_login(user_name=user_name, ip=client.address[0], port=client.address[1], status=user_status)
            # добавляем соединение клиента в очередь
            if client not in self.outputs:
                self.outputs.append(client)
            return True
        return False

    def _remove_client(self, client: Endpoint):
        self.logger.info(f'Client {client} disconnected')
        if client in self.clients:
            cl = self.clients.pop(client)
            self.db.cl_user_logout(user_name=cl)
        if client in self.outputs:
            self.outputs.remove(client)
        if client in self.inputs:
            self.inputs.remove(client)
        if client:
            client.close()

    def _register_message(self, msg: ActionMessage):
        id = self.db.cl_message_add(
            receiver_name=msg.receiver,
            sender_name=msg.sender,
            dt_time=datetime.fromtimestamp(msg.time),
            msg_txt=msg.message  # type: ignore
        )
        self.messages[id] = msg

    def _set_message_delivered(self, msg_id):
        self.db.cl_message_mark_delivered(msg_id)
        self.messages.pop(msg_id, None)

    def run(self, terminate_on: threading.Event, mainloop_timeout=1):
        try:

            self.conn.start_server(self.config.host, self.config.port,  # type: ignore
                                   self.config.connection_limit,
                                   self.config.timeout)

            self.inputs.append(self.conn)  # сокеты, которые будем читать
            self.messages = {}  # здесь будем хранить сообщения для сокетов, по идее надо из базы инициализировать...

            while not terminate_on.isSet():
                reads, send, excepts = select.select(self.inputs, self.outputs, self.inputs, mainloop_timeout)

                # список READS - сокеты, готовые к чтению
                for client in reads:
                    if client == self.conn:
                        # на серверный сокет приходит запрос на подключение клиента
                        self._add_client(self.conn.get_client())
                        # new_conn.setblocking(False)
                    else:
                        # читаем сообщение
                        try:
                            action = self._read_message(client)
                        except (JIMSerializerError, JIMValidationError):
                            try:
                                self._send_response(client, Response400())
                            except Exception as e:
                                # Клиент отключился
                                self._remove_client(client)
                        except Exception as e:
                            # Клиент отключился
                            self._remove_client(client)
                        else:
                            try:
                                if action.action == ActionPresence.get_action():
                                    try:
                                        is_ok = self._auth_client(client, action.user_account, action.user_status)  # type: ignore
                                    except Exception as e:
                                        self.logger.error(f'error on presence {e}')
                                        self._send_response(client, Response400('Server error'))
                                    else:
                                        if is_ok:
                                            self._send_response(client, Response200())
                                        else:
                                            self._send_response(client, Response400('Already exists'))

                                elif action.action == ActionMessage.get_action():
                                    try:
                                        self._register_message(action)  # type: ignore
                                    except Exception as e:
                                        self._send_response(client, Response400(error=str(e)))
                                    else:
                                        self._send_response(client, Response200())

                                elif action.action == ActionGetContacts.get_action():
                                    try:
                                        contacts = self.db.cl_user_contact_get_list(user_name=action.user_account)  # type: ignore
                                    except Exception as e:
                                        self._send_response(client, Response400(error=str(e)))
                                    else:
                                        self._send_response(client, Response202(contacts))

                                elif action.action == ActionAddContact.get_action():
                                    try:
                                        if action.user_account == action.contact:
                                            self._send_response(client, Response400(error="Can't add yourself as a contact"))
                                        else:
                                            contacts = self.db.cl_user_contact_add(user_name=action.user_account, contact_name=action.contact)  # type: ignore
                                    except Exception as e:
                                        self._send_response(client, Response400(error=str(e)))
                                    else:
                                        self._send_response(client, Response200())

                                elif action.action == ActionDeleteContact.get_action():
                                    try:
                                        contacts = self.db.cl_user_contact_delete(user_name=action.user_account, contact_name=action.contact)  # type: ignore
                                    except Exception as e:
                                        self._send_response(client, Response400(error=str(e)))
                                    else:
                                        self._send_response(client, Response200())

                                elif action.action == ActionExit.get_action():
                                    self._send_response(client, Response200())
                                    time.sleep(1)
                                    self._remove_client(client)
                            except Exception as e:
                                self.logger.error(f'Error {e} accepting message {action} from {self.clients.get(client)}')
                                # Клиент отключился
                                self._remove_client(client)

                # список SEND - сокеты, готовые принять сообщение
                if self.messages:
                    msg_dict = self.messages.copy()
                else:
                    msg_dict = {}
                for message_id, message in msg_dict.items():
                    clients_ = []
                    for client, user_name in self.clients.items():
                        if user_name == message.receiver and client in send:
                            clients_.append(client)
                    # clients_ = [client for client, user_name in self.clients if user_name == message.receiver]
                    for client in clients_:  # should be only one
                        if client in send:
                            try:
                                response = self._send_message(client, message)
                                if not response.is_error:
                                    self._set_message_delivered(message_id)
                            except (JIMSerializerError, JIMValidationError) as e:
                                self.logger.error(f'Serialization error {e} while sending message to {client}')
                            except Exception as e:
                                # Клиент отключился
                                self._remove_client(client)

                # список EXCEPTS - сокеты, в которых произошла ошибка
                for client in excepts:
                    self._remove_client(client)

        except Exception as e:
            self.logger.critical(f'Server error {e}')
        finally:
            self.conn.close()
