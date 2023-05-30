# Server app
# server.py -p 8080 -a 127.0.0.1
import argparse
import os
import socket
import time

from gb_python_async01.config import BaseConfig
from gb_python_async01.serializers import JIMSerializerError, decode_message, encode_message
from gb_python_async01.serializers import ProtocolJIM as prot

config = BaseConfig


def process_request(request):
    _action = request.get(prot.action)
    _time = request.get(prot.time)
    _user = request.get(prot.user)
    if _action and _time and _user and _action in prot.actions.keys():
        return {
            prot.response: 200,
            prot.time: time.time()
        }
    return {
        prot.response: 400,
        prot.time: time.time(),
        prot.error: 'Bad Request'
    }


def init_socket():
    parser = argparse.ArgumentParser(description='Server arguments')
    parser.add_argument('-p', '--port', type=int, help='Port')
    parser.add_argument('-a', '--host', type=str, help='Host')
    args = parser.parse_args()

    srv_host = args.host or config.SERVER_HOST_DEFAULT
    srv_port = args.port or config.SERVER_PORT_DEFAULT

    srv_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    if srv_socket:
        try:
            srv_socket.bind((srv_host, srv_port))
            srv_socket.listen(config.CONNECTION_LIMIT)  # type: ignore

            return srv_socket
        except Exception as e:
            srv_socket.close()
            print(f'Initialization error{e}')
            return None


def run(s):
    while True:
        client, client_address = s.accept()
        try:
            message = client.recv(config.MESSAGE_MAX_SIZE)
            request = decode_message(message)

            response = process_request(request)
            print(f'{request} => {response}')
            message = encode_message(response)
            client.send(message)
        except JIMSerializerError:
            print('Serialization error')
        finally:
            client.close()


def main():
    s = init_socket()
    if s:
        try:
            run(s)
        finally:
            s.close()


if __name__ == '__main__':
    main()
