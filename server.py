# Server app
# server.py -p 8080 -a 127.0.0.1
import argparse

from config import *
from gb_python_async01.server.app import ServerApp
from gb_python_async01.server.config import ServerConfig

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Server arguments')
    parser.add_argument('-p', '--port', type=int, help='Server port')
    parser.add_argument('-a', '--host', type=str, help='Server host')
    parser.add_argument('-s', '--silent', type=bool, help='Start without GUI')
    parser.add_argument('-d', '--db_url', type=str, help='DB connect string')
    args = parser.parse_args()

    config = ServerConfig(DevConfig)
    if args.host:
        config.host = args.host
    if args.port:
        config.port = args.port
    if args.silent:
        config.gui_enabled = False
    if args.db_url:
        config.db_url = args.db_url

    ServerApp(config).run()
