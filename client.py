# client.py 127.0.0.1 8081
import argparse
import sys
import time
from gb_python_async01.common.errors import EndpointCommunicationError, JIMSerializerError, JIMValidationError
from gb_python_async01.common.model.message import Action, ActionMessage, ActionPresence, Response, Response200
from config import *
from gb_python_async01.devutils.debug_decorators import Log
from gb_python_async01.log.config_client import init_logger
from gb_python_async01.common.endpoints import ClientEndpoint
from gb_python_async01.common.JIM import JIMSerializer


class Client():
    def __init__(self, mode):
        self.config = DevConfig
        self.logger = init_logger(self.config.DEBUG, self.config.TESTING)
        self.user = self.config.ANONIMOUS_USER
        self.serializer = JIMSerializer()
        self.mode = mode

    def _send_message(self, msg: Action) -> Response:
        self.logger.debug(f'Sending {msg}')
        self.conn.put_message(self.serializer.encode_action(msg))
        response = self.serializer.decode_response(self.conn.get_message())
        self.logger.debug(f'Response {response}')
        return response

    def _read_message(self) -> Action:
        action = self.serializer.decode_action(self.conn.get_message())
        self.logger.debug(f'Accepting {action}')
        self.conn.put_message(self.serializer.encode_response(Response200()))
        return action

    def run(self, srv_host, srv_port: int):
        self.host = srv_host or self.config.SERVER_HOST_DEFAULT
        self.port = srv_port or self.config.SERVER_PORT_DEFAULT
        self.conn = ClientEndpoint(logger=self.logger, message_max_size=self.config.MESSAGE_MAX_SIZE)

        try:
            self.logger.info(f'Connecting to {self.host}:{self.port}, mode {mode}')
            self.conn.connect_to_server(host=self.host, port=self.port)

            action = ActionPresence(time=time.time(),
                                    user_account=self.user,
                                    user_status=f'{self.user} is here')
            response = self._send_message(action)
            if response.is_error:
                self.logger.info(f'Error response on presence message: {response}')
            else:
                while mode == 'r':
                    action = self._read_message()
                    # CLI / GUI serializer (?)
                    if action.action == ActionMessage.get_action():
                        print(f'{action.sender}: {action.message}')
                while mode == 'w':
                    # CLI / GUI serializer (?)
                    msg_txt = input('Введите сообщение в чат: ')
                    action = ActionMessage(time=time.time(),
                                           message=msg_txt,
                                           sender=self.user,
                                           receiver='')
                    response = self._send_message(action)
                    if response.is_error:
                        self.logger.info(f'Error response {response}')

        except EndpointCommunicationError as e:
            self.logger.critical(e)
        except JIMSerializerError as e:
            self.logger.critical(e)
        except JIMValidationError as e:
            self.logger.critical(e)
        finally:
            self.conn.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Client arguments')
    parser.add_argument('-m', '--mode', type=str, help='Mode (w, r)')
    parser.add_argument('-p', '--port', type=int, help='Server port')
    parser.add_argument('-a', '--host', type=str, help='Server host')
    args = parser.parse_args()
    mode = args.mode or 'r'
    Client(mode).run(args.host, args.port)
