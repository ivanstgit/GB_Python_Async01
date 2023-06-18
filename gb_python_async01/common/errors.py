from typing import Any


class JIMNotImplementedError(NotImplementedError):
    pass


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
        'Serialization error'


class EndpointCommunicationError(Exception):
    def __str__(self):
        'Communication error'
