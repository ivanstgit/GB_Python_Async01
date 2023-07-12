"""Модуль с классами исключений при клиент-серверном взаимодействии"""


class TransportError(Exception):
    """Базовый класс исключений"""

    def __str__(self):
        return self.__doc__ or self.__class__.__name__


class JIMError(TransportError):
    """Базовый класс для исключений транспортного протокола"""


class JIMNotImplementedError(JIMError):
    """Метод протокола не поддерживается"""


class JIMValidationError(JIMError):
    """Ошибка протокола (структуры сообщения)"""

    def __init__(self, *args: object, field=None) -> None:
        super().__init__(*args)
        self._field = field

    def __str__(self):
        if self._field:
            return f"JIM Validation error: invalid field {self._field}"

        return super().__str__()


class JIMSerializerError(JIMError):
    """Ошибка при сериализации сообщения"""


class EndpointError(TransportError):
    """Ошибка при передаче данных"""


class EndpointCommunicationError(EndpointError):
    """Ошибка соединения"""


class EndpointTimeout(EndpointError):
    """Таймаут"""


class EndpointParamError(EndpointError):
    """Ошибка в параметрах сокета"""

    def __init__(self, *args: object, param=None, error_desc="") -> None:
        super().__init__(*args)
        self._param = param
        self._error_desc = error_desc

    def __str__(self):
        if self._param:
            return f"Endpoint invalid parameter {self._param}: {self._error_desc}"

        return super().__str__()


class TransportSecurityError(TransportError):
    """Ошибка безопасности передачи данных"""


class TransportSecurityNoSessionKeyError(TransportSecurityError):
    """Отсутствует сессионный ключ"""


class TransportSecurityValidationError(TransportSecurityError):
    """Содержимое сообщения не соответствует подписи"""


class TransportSecurityAuthError(TransportSecurityError):
    """Ошибка аутентификации"""
