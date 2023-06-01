# client.py 127.0.0.1 8081
import socket
import sys
import time
from gb_python_async01.config import BaseConfig
from gb_python_async01.serializers import JIMSerializerError, ProtocolSerializerError, decode_message, encode_message
from gb_python_async01.serializers import ProtocolJIM as prot

config = BaseConfig


def init_socket(srv_host=config.SERVER_HOST_DEFAULT, srv_port=config.SERVER_PORT_DEFAULT):
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
        s = init_socket(srv_host=srv_host, srv_port=srv_port)
    else:
        s = init_socket()

    if s:
        try:
            request = generate_presence()
            # print(request)
            message = encode_message(request)
            s.send(message)

            message = s.recv(config.MESSAGE_MAX_SIZE)
            response = decode_message(message)
            # print(response)
            print(process_response(response))

        except JIMSerializerError:
            print('Serialization error')
        finally:
            s.close()


if __name__ == '__main__':
    main()
