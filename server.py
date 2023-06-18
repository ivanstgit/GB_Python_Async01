# Server app
# server.py -p 8080 -a 127.0.0.1
import argparse
import select
import socket
import time

from config import *
from gb_python_async01.common.endpoints import *
from gb_python_async01.common.model.message import *
from gb_python_async01.common.JIM import JIMSerializer
from gb_python_async01.common.errors import EndpointCommunicationError, JIMSerializerError, JIMValidationError

from gb_python_async01.devutils.debug_decorators import Log
from gb_python_async01.log.config_server import init_logger


class Server():
    def __init__(self):
        self.config = DevConfig
        self.logger = init_logger(self.config.DEBUG, self.config.TESTING)
        self.serializer = JIMSerializer()
        self.conn = ServerEndpoint(logger=self.logger, message_max_size=self.config.MESSAGE_MAX_SIZE)

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

    def run(self, srv_host, srv_port: int):
        self.host = srv_host or self.config.SERVER_HOST_DEFAULT
        self.port = srv_port or self.config.SERVER_PORT_DEFAULT

        try:
            self.conn.start_server(self.host, self.port,
                                   self.config.SERVER_CONNECTION_LIMIT,
                                   self.config.SERVER_TIMEOUT)
            self.inputs = []
            self.inputs.append(self.conn)  # сокеты, которые будем читать
            self.outputs = []  # сокеты, в которые надо писать
            self.messages = {}  # здесь будем хранить сообщения для сокетов

            while True:
                reads, send, excepts = select.select(self.inputs, self.outputs, self.inputs)

                # список READS - сокеты, готовые к чтению
                for conn in reads:
                    if conn == self.conn:
                        # на серверный сокет приходит запрос на подключение клиента
                        client = self.conn.get_client()
                        # НЕ устанавливаем неблокирующий сокет
                        # new_conn.setblocking(False)
                        self.inputs.append(client)

                    else:
                        # читаем сообщение
                        client = conn
                        try:
                            action = self._read_message(client)
                            self._send_response(client, Response200())
                            if action.action == ActionMessage.get_action():
                                if self.messages.get(client, None):
                                    self.messages[client].append(action)
                                else:
                                    self.messages[client] = [action]
                            elif action.action == ActionPresence.get_action():
                                # добавляем соединение клиента в очередь
                                if client not in self.outputs:
                                    self.outputs.append(client)
                        except (JIMSerializerError, JIMValidationError):
                            self._send_response(conn, Response400())
                        except Exception as e:
                            # Клиент отключился
                            self.logger.info(f'Client {client} disconnected')
                            if client in self.outputs:
                                self.outputs.remove(client)
                            if client in self.inputs:
                                self.inputs.remove(client)
                            if client:
                                client.close()

                # список SEND - сокеты, готовые принять сообщение
                if self.messages:
                    for conn in send:
                        client = conn
                        for sender, messages in self.messages.items():
                            for message in messages:
                                try:
                                    if sender != client:
                                        response = self._send_message(client, message)
                                except (JIMSerializerError, JIMValidationError) as e:
                                    self.logger.error(f'Serialization error {e} while sending message to {client}')
                                except OSError:
                                    pass
                    self.messages = {}

                # список EXCEPTS - сокеты, в которых произошла ошибка
                for conn in excepts:
                    client = conn
                    # Клиент отключился
                    self.logger.info(f'Client {client} disconnected')
                    if client in self.outputs:
                        self.outputs.remove(client)
                    if client in self.inputs:
                        self.inputs.remove(client)
                    if client:
                        client.close()

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
