""" Очередное задание в рамках изучения Python, не имеющее отношения к проекту
# Т.к. в текущей реализации сокеты изолированы абстракцией Endpoint, то применяем требование к ClientEndpoint / ServerEndpoint
# Требование 1.3 не понятно...

# 1. Реализовать метакласс ClientVerifier, выполняющий базовую проверку класса «Клиент» (для некоторых проверок уместно использовать модуль dis):
# отсутствие вызовов accept и listen для сокетов;
# использование сокетов для работы по TCP;
# отсутствие создания сокетов на уровне классов, то есть отсутствие конструкций такого вида: class Client: s = socket() ...
# 2. Реализовать метакласс ServerVerifier, выполняющий базовую проверку класса «Сервер»:
# отсутствие вызовов connect для сокетов;
# использование сокетов для работы по TCP.
"""

import dis
from typing import Any


def parse_code(clsdict):
    """Список методов, которые используются в функциях класса"""
    methods = []
    attributes = []
    for func in clsdict:
        try:
            ret = dis.get_instructions(clsdict[func])
        except (TypeError, IndentationError, SyntaxError):
            pass
        else:
            for i in ret:
                # print(i)
                if i.opname in ("LOAD_GLOBAL", "LOAD_METHOD"):
                    if i.argval not in methods:
                        methods.append(i.argval)
                if i.opname in ("LOAD_ATTR"):
                    if i.argval not in attributes:
                        attributes.append(i.argval)
    return methods, attributes


class EndpointVerifier(type):
    def __init__(self, clsname, bases, clsdict):
        if not bases:
            methods, attributes = parse_code(clsdict)

            # использование сокетов для работы по TCP;
            if "socket" not in methods:
                raise TypeError("Отсутствуют вызовы функций, работающих с сокетами.")

            if not ("SOCK_STREAM" in attributes and "AF_INET" in attributes):
                raise TypeError("Некорректная инициализация сокета.")

        super().__init__(clsname, bases, clsdict)


class ClientEndpointVerifier(EndpointVerifier):
    def __init__(self, clsname, bases, clsdict):
        methods, attributes = parse_code(clsdict)

        # отсутствие вызовов accept и listen для сокетов;
        for command in ("accept", "listen"):
            if command in methods:
                raise TypeError(
                    f"В классе обнаружено использование запрещённого метода {command}"
                )

        # использование сокетов для работы по TCP;
        if "connect" not in methods:
            raise TypeError("Отсутствуют вызовы функций, работающих с сокетами.")
        super().__init__(clsname, bases, clsdict)


class ServerEndpointVerifier(EndpointVerifier):
    def __init__(self, clsname, bases, clsdict):
        methods, attributes = parse_code(clsdict)

        # отсутствие вызовов connect для сокетов;
        for command in "connect":
            if command in methods:
                raise TypeError(
                    f"В классе обнаружено использование запрещённого метода {command}"
                )

        # использование сокетов для работы по TCP;
        for command in ("accept", "listen"):
            if command not in methods:
                raise TypeError("Отсутствуют вызовы функций, работающих с сокетами.")

        super().__init__(clsname, bases, clsdict)
