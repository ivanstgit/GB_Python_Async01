import socket
from gb_python_async01.transport.errors import EndpointParamError


class EndpointPort:
    min_value = 1024
    max_value = 65535

    def __set__(self, instance, value):
        if not self.min_value <= value <= self.max_value:
            raise EndpointParamError(
                param=self.name,
                error_desc=f'Попытка запуска сервера с указанием неподходящего порта {value}. Допустимы адреса с {self.min_value} до {self.max_value}.')
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
