# client.py -h 127.0.0.1 -p 8081 -u guest01
import argparse

from config import *
from gb_python_async01.client.app import ClientApp
from gb_python_async01.client.config import ClientConfig


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Client arguments')
    parser.add_argument('-u', '--user', type=str, help='User name')
    parser.add_argument('-p', '--port', type=int, help='Server port')
    parser.add_argument('-a', '--host', type=str, help='Server host')
    args = parser.parse_args()

    user_name = args.user or DevConfig.ANONIMOUS_USER
    config = ClientConfig(user_name, DevConfig)
    if args.host:
        config.host = args.host
    if args.port:
        config.port = args.port

    ClientApp(config).run()
