# Server app
# server.py -p 8080 -a 127.0.0.1
import argparse
import os
import socket
import sys
import time


from config import *
from log.config_server import init_logger
from common.serializers import JIMSerializerError, decode_message, encode_message
from common.serializers import ProtocolJIM as prot

config = DevConfig
logger = init_logger(config.DEBUG, config.TESTING)


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


def init_socket(srv_host, srv_port):
    srv_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv_socket.bind((srv_host, srv_port))
    srv_socket.listen(config.CONNECTION_LIMIT)
    return srv_socket


def run(s):
    while True:
        client, client_address = s.accept()
        try:
            message = client.recv(config.MESSAGE_MAX_SIZE)
            request = decode_message(message)

            response = process_request(request)
            logger.debug(f'{client_address}: {request} => {response}')
            message = encode_message(response)
            client.send(message)
        except JIMSerializerError:
            logger.critical('Serialization error')
        finally:
            client.close()


def main():
    parser = argparse.ArgumentParser(description='Server arguments')
    parser.add_argument('-p', '--port', type=int, help='Port')
    parser.add_argument('-a', '--host', type=str, help='Host')
    args = parser.parse_args()

    srv_host = args.host or config.SERVER_HOST_DEFAULT
    srv_port = args.port or config.SERVER_PORT_DEFAULT

    s = None
    try:
        logger.info(f'Starting server on {srv_host}:{srv_port}')
        s = init_socket(srv_host, srv_port)
        run(s)
    except Exception as e:
        logger.critical(f'Initialization error{e}')
    finally:
        if s:
            s.close()


if __name__ == '__main__':
    main()
