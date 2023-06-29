from typing import Any


class JIMNotImplementedError(NotImplementedError):
    def __str__(self):
        return f'Action or Response code is not implemented'


class JIMValidationError(Exception):
    def __init__(self, *args: object, field=None) -> None:
        super().__init__(*args)
        self._field = field

    def __str__(self):
        if self._field:
            return f'JIM Validation error: invalid field {self._field}'

        return f'JIM Validation error'


class JIMSerializerError(Exception):
    def __str__(self):
        return 'Serialization error'


class EndpointCommunicationError(Exception):
    def __str__(self):
        return 'Communication error'


class EndpointTimeout(Exception):
    def __str__(self):
        return 'timeout'


class EndpointParamError(Exception):
    def __init__(self, *args: object, param=None, error_desc='') -> None:
        super().__init__(*args)
        self._param = param
        self._error_desc = error_desc

    def __str__(self):
        if self._param:
            return f'Endpoint invalid parameter {self._param}: {self._error_desc}'

        return f'EndpointParamError'
