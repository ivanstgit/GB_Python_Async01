"""Модуль для запуска сервера"""
import argparse

from config import BaseConfig, DevConfig, TestingConfig
from gb_python_async01.server.app import ServerApp
from gb_python_async01.server.cli import ServerCLI
from gb_python_async01.server.config import ServerConfig

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Server commands")
    parser.add_argument("-d", "--db_url", type=str, help="DB connect string")
    subparsers = parser.add_subparsers(
        title="subcommands",
        description="valid subcommands",
        help="additional help",
        dest="command",
    )

    parser.add_argument("-p", "--port", type=int, help="Listen port")
    parser.add_argument("-a", "--host", type=str, help="Listen host")
    parser.add_argument("-s", "--silent", action="store_true", help="Start without GUI")

    parser_db_init = subparsers.add_parser("db_init", help="init db tables")

    parser_user_add = subparsers.add_parser("user_add", help="add user")
    parser_user_add.add_argument(
        "-l", "--login", type=str, help="User login", required=True
    )
    parser_user_add.add_argument(
        "-p", "--password", type=str, help="User password", required=True
    )

    args = parser.parse_args()

    config = ServerConfig(DevConfig)
    if args.db_url:
        config.db_url = args.db_url

    if args.command == "db_init":
        cli = ServerCLI(config)
        cli.init_db_tables()
    elif args.command == "user_add":
        cli = ServerCLI(config)
        cli.add_user(args.login, args.password)
    else:
        if args.host:
            config.host = args.host
        if args.port:
            config.port = args.port
        if args.silent:
            config.gui_enabled = False
        ServerApp(config).run()
