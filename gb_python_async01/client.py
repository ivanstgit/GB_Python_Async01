# client.py 127.0.0.1 8081
import os
import socket
import sys
import time

from config import *
from log.config_client import init_logger
from common.serializers import JIMSerializerError, ProtocolSerializerError, decode_message, encode_message
from common.serializers import ProtocolJIM as prot

config = DevConfig
logger = init_logger(config.DEBUG, config.TESTING)


def init_socket(srv_host, srv_port):
    # по логике это надо в отдельный класс выносить, но в ТЗ требуют функций...
    # а в примере вообще логика взаимодействия через сокет по разным модулям/пакетам разнесена...
    srv_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv_socket.connect((srv_host, srv_port))
    return srv_socket


def generate_presence():
    return {
        prot.action: 'presence',
        prot.time: time.time(),
        prot.user: {
            prot.user_account: 'guest'
        }
    }


def process_response(r):
    _response = r.get(prot.response)
    _time = r.get(prot.time)
    _error = r.get(prot.error)
    if _response and not _error:
        return _response
    return f'{_response}: {_error}'


def main():

    if len(sys.argv) > 2:
        srv_host = sys.argv[1]
        srv_port = int(sys.argv[2])
    else:
        srv_host = config.SERVER_HOST_DEFAULT
        srv_port = config.SERVER_PORT_DEFAULT

    s = None
    try:
        logger.info(f'Connecting to {srv_host}:{srv_port}')
        s = init_socket(srv_host=srv_host, srv_port=srv_port)

        request = generate_presence()
        logger.debug(f' request: {request}')
        message = encode_message(request)
        s.send(message)

        message = s.recv(config.MESSAGE_MAX_SIZE)
        response = decode_message(message)
        logger.debug(f' response: {process_response(response)}')

    except ConnectionRefusedError as e:
        logger.critical(f'Connection error {e}')
    except JIMSerializerError:
        logger.critical('Serialization error')
    finally:
        if s:
            s.close()


if __name__ == '__main__':
    main()
