# client.py -h 127.0.0.1 -p 8081 -u guest01
import argparse
import sys
import threading
import time
from gb_python_async01.common.errors import *
from gb_python_async01.common.model.message import *
from config import *
from gb_python_async01.devutils.debug_decorators import Log
from gb_python_async01.log.config_client import init_logger
from gb_python_async01.common.endpoints import ClientEndpoint
from gb_python_async01.common.JIM import JIMSerializer


class Client():
    def __init__(self, username):
        self.config = DevConfig
        self.logger = init_logger(self.config.DEBUG, self.config.TESTING)
        self.user = username or self.config.ANONIMOUS_USER
        self.serializer = JIMSerializer()
        self.lock = None
        self.waiting_time = 0.1

    def _send_message(self, msg: Action) -> Response:
        self.logger.debug(f'{self.user} Sending {msg}')
        self.conn.put_message(self.serializer.encode_action(msg))
        response = self.serializer.decode_response(self.conn.get_message())
        self.logger.debug(f'{self.user} Response {response}')
        return response

    def _read_message(self) -> Action:
        action = self.serializer.decode_action(self.conn.get_message())
        self.logger.debug(f'{self.user} Accepting {action}')
        self.conn.put_message(self.serializer.encode_response(Response200()))
        return action

    def reader_loop(self, lock: threading.Lock, timeout=0.5):
        while True:
            time.sleep(timeout)
            if not lock.locked():
                # self.logger.debug(f'{self.user} Reader: try to lock {lock.locked()}')
                with lock:
                    # self.logger.debug(f'{self.user} Reader: get lock {lock.locked()}')
                    try:
                        action = self._read_message()
                    except EndpointTimeout:
                        pass
                    else:
                        # CLI / GUI serializer (?)
                        if action.action == ActionMessage.get_action():
                            print(f'{action.sender}: {action.message}')
                # self.logger.debug(f'{self.user} Reader: unlocked {lock.locked()}')
            time.sleep(self.waiting_time)

    def sender_loop(self, lock: threading.Lock):
        while True:
            # CLI / GUI serializer (?)
            EXIT_MESSAGE = 'exit'
            msg_txt = input(f'Введите сообщение в чат ({EXIT_MESSAGE} для выхода): ')
            if msg_txt == '':
                continue
            elif msg_txt == EXIT_MESSAGE:
                action = ActionExit(time=time.time())
            else:
                receiver = input(f'Введите адресата: ')
                action = ActionMessage(time=time.time(),
                                       message=msg_txt,
                                       sender=self.user,
                                       receiver=receiver)
            # self.logger.debug(f'{self.user} Sender: try to lock {lock.locked()}')
            with lock:
                # self.logger.debug(f'{self.user} Sender: locked {lock.locked()}')
                response = self._send_message(action)
            # self.logger.debug(f'{self.user} Sender: unlocked {lock.locked()}')

            if response.is_error:
                self.logger.info(f'{self.user} Error response {response}')
            if action.action == ActionExit.get_action():
                break
            time.sleep(self.waiting_time)

    def run(self, srv_host, srv_port: int):
        self.host = srv_host or self.config.SERVER_HOST_DEFAULT
        self.port = srv_port or self.config.SERVER_PORT_DEFAULT
        self.conn = ClientEndpoint(logger=self.logger, message_max_size=self.config.MESSAGE_MAX_SIZE)

        try:
            # Connecting to server
            self.logger.info(f'Connecting to {self.host}:{self.port}, user {self.user}')
            # Reading and writing in one socket -> timeout needed for resource lock releasing
            self.conn.connect_to_server(host=self.host, port=self.port, timeout=1)

            # Presence (identification) message generation
            action = ActionPresence(time=time.time(),
                                    user_account=self.user,
                                    user_status=f'{self.user} is here')
            response = self._send_message(action)
            if response.is_error:
                self.logger.info(f'{self.user} Error response on presence message: {response}')
            else:
                # Starting interaction threads
                print(f'Welcome, {self.user}')

                lock = threading.Lock()

                thread_reader = threading.Thread(target=self.reader_loop, name='Reader', args=(lock,))
                thread_reader.daemon = True
                thread_reader.start()
                self.logger.debug(f'{self.user} Reader thread started')

                time.sleep(0.5)
                thread_sender = threading.Thread(target=self.sender_loop, name='Sender', args=(lock,))
                thread_sender.daemon = True
                thread_sender.start()
                self.logger.debug(f'{self.user} Sender thread started')

                # Main loop
                while True:
                    time.sleep(1)
                    if thread_sender.is_alive() and thread_reader.is_alive():
                        continue
                    self.logger.debug(f'{self.user} Client stopped...')
                    break

        except EndpointCommunicationError as e:
            self.logger.critical(e)
        except JIMSerializerError as e:
            self.logger.critical(e)
        except JIMValidationError as e:
            self.logger.critical(e)
        except Exception as e:
            self.logger.critical(e)
        finally:
            self.conn.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Client arguments')
    parser.add_argument('-u', '--user', type=str, help='User name')
    parser.add_argument('-p', '--port', type=int, help='Server port')
    parser.add_argument('-a', '--host', type=str, help='Server host')
    args = parser.parse_args()
    Client(args.user).run(args.host, args.port)
