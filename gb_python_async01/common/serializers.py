import json

MESSAGE_ENCODING = 'utf-8'


class ProtocolJIM():
    action = 'action'
    actions = {
        'presence': 'присутствие. Сервисное сообщение для извещения сервера о присутствии клиента online',
        'prоbe': 'проверка присутствия. Сервисное сообщение от сервера для проверки присутствии клиента online',
        'msg': 'простое сообщение пользователю или в чат',
        'quit': 'отключение от сервера',
        'authenticate': 'авторизация на сервере',
        'join': 'присоединиться к чату',
        'leave': 'покинуть чат',
    }
    time = 'time'
    user = 'user'
    user_account = 'account_name'

    response = 'response'
    error = 'error'


class JIMSerializerError(Exception):
    pass


class ProtocolSerializerError(Exception):
    pass


def decode_message(message):
    try:
        return json.loads(message.decode(MESSAGE_ENCODING))
    except Exception as e:
        raise JIMSerializerError(e)


def encode_message(message):
    try:
        return json.dumps(message).encode(MESSAGE_ENCODING)
    except Exception as e:
        raise JIMSerializerError(e)
