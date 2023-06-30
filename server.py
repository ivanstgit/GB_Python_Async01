# Server app
# server.py -p 8080 -a 127.0.0.1
import argparse

from config import *
from gb_python_async01.server.app import ServerApp
from gb_python_async01.server.config import ServerConfig

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Server arguments')
    parser.add_argument('-p', '--port', type=int, help='Port')
    parser.add_argument('-a', '--host', type=str, help='Host')
    args = parser.parse_args()

    config = ServerConfig(DevConfig)
    if args.host:
        config.host = args.host
    if args.port:
        config.port = args.port

    ServerApp(config).run()
