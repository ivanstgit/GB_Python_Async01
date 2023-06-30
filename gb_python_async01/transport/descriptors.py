import socket
from gb_python_async01.transport.errors import EndpointParamError


class EndpointPort:
    def __set__(self, instance, value):
        if not 1023 < value < 65536:
            raise EndpointParamError(param=self.name,
                                     error_desc=f'Попытка запуска сервера с указанием неподходящего порта {value}. Допустимы адреса с 1024 до 65535.')
        instance.__dict__[self.name] = value

    def __set_name__(self, owner, name):
        self.name = name


class EndpointHost:
    def __set__(self, instance, value):
        try:
            socket.inet_aton(value)
        except socket.error:
            raise EndpointParamError(param=self.name,
                                     error_desc=f'Попытка запуска сервера с указанием неподходящего адреса {value}. ')
        instance.__dict__[self.name] = value

    def __set_name__(self, owner, name):
        self.name = name
