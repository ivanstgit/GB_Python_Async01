# Server app
# server.py -p 8080 -a 127.0.0.1
import argparse
import select
import time

from config import *
from gb_python_async01.common.descriptors import EndpointHost, EndpointPort
from gb_python_async01.common.endpoints import *
from gb_python_async01.common.model.message import *
from gb_python_async01.common.JIM import JIMSerializer
from gb_python_async01.common.errors import EndpointCommunicationError, JIMSerializerError, JIMValidationError

from gb_python_async01.devutils.debug_decorators import Log
from gb_python_async01.log.config_server import init_logger


class Server():
    port = EndpointPort()
    host = EndpointHost()

    def __init__(self):
        self.config = DevConfig
        self.logger = init_logger(self.config.DEBUG, self.config.TESTING)
        self.serializer = JIMSerializer()
        self.conn = ServerEndpoint(logger=self.logger, message_max_size=self.config.MESSAGE_MAX_SIZE)
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

    def _auth_client(self, client: Endpoint, username: str) -> bool:
        if client in self.clients and (not username in self.clients.values()):
            self.logger.info(f'Client {client} authorized with name {username}')
            self.clients[client] = username
            # добавляем соединение клиента в очередь
            if client not in self.outputs:
                self.outputs.append(client)
            return True
        return False

    def _remove_client(self, client: Endpoint):
        self.logger.info(f'Client {client} disconnected')
        if client in self.clients:
            self.clients.pop(client)
        if client in self.outputs:
            self.outputs.remove(client)
        if client in self.inputs:
            self.inputs.remove(client)
        if client:
            client.close()

    def run(self, srv_host, srv_port: int):
        try:
            self.host = srv_host or self.config.SERVER_HOST_DEFAULT
            self.port = srv_port or self.config.SERVER_PORT_DEFAULT

            self.conn.start_server(self.host, self.port,
                                   self.config.SERVER_CONNECTION_LIMIT,
                                   self.config.SERVER_TIMEOUT)

            self.inputs.append(self.conn)  # сокеты, которые будем читать
            self.messages = {}  # здесь будем хранить сообщения для сокетов

            while True:
                reads, send, excepts = select.select(self.inputs, self.outputs, self.inputs)

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
                                if action.action == ActionMessage.get_action():
                                    if self.messages.get(client, None):
                                        self.messages[client].append(action)
                                    else:
                                        self.messages[client] = [action]
                                    self._send_response(client, Response200())
                                elif action.action == ActionPresence.get_action():
                                    if self._auth_client(client, action.user_account):  # type: ignore
                                        self._send_response(client, Response200())
                                    else:
                                        self._send_response(client, Response400('Already exists'))
                                elif action.action == ActionExit.get_action():
                                    self._remove_client(client)
                            except Exception as e:
                                # Клиент отключился
                                self._remove_client(client)

                # список SEND - сокеты, готовые принять сообщение
                if self.messages:
                    for client in send:
                        for sender, messages in self.messages.items():
                            for message in messages:
                                try:
                                    if sender != client and (message.receiver in ['', self.clients.get(client)]):
                                        response = self._send_message(client, message)
                                except (JIMSerializerError, JIMValidationError) as e:
                                    self.logger.error(f'Serialization error {e} while sending message to {client}')
                                except Exception as e:
                                    # Клиент отключился
                                    self._remove_client(client)
                    self.messages = {}

                # список EXCEPTS - сокеты, в которых произошла ошибка
                for client in excepts:
                    self._remove_client(client)

        except Exception as e:
            self.logger.critical(f'Server error {e}')
        finally:
            self.conn.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Server arguments')
    parser.add_argument('-p', '--port', type=int, help='Port')
    parser.add_argument('-a', '--host', type=str, help='Host')
    args = parser.parse_args()
    Server().run(args.host, args.port)
