# Точка входа/ лаунчер для клиентской части
# Все параметры необязательные, но хост и порт сервера можно задать только при запуске
# client.py -a 127.0.0.1 -b 8081 -u ttttest -p ttttest
import argparse

from config import *
from gb_python_async01.client.app import ClientApp
from gb_python_async01.client.config import ClientConfig


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Client arguments')
    parser.add_argument('-u', '--user', type=str, help='User name')
    parser.add_argument('-p', '--password', type=str, help='User password')
    parser.add_argument('-a', '--host', type=str, help='Server host')
    parser.add_argument('-b', '--port', type=int, help='Server port')
    args = parser.parse_args()

    config = ClientConfig(DevConfig)
    if args.host:
        config.host = args.host
    if args.port:
        config.port = args.port

    ClientApp(config).run(args.user, args.password)
