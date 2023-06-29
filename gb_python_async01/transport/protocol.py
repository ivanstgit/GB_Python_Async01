# Transport protocol and serialization
# Не понятно по архитектуре пока - в асинхронном режиме будет ли на action response или может быть следующее сообщение7
# Вообще без идентификатора сообщения на сервере только первый вариант
import json

from gb_python_async01.transport.errors import *
from gb_python_async01.transport.model.message import *
from gb_python_async01.transport.serializers.message import *

MESSAGE_ENCODING = 'utf-8'


class MessageSerializerFactory():
    methods = {
        MessageSerializer.action: {
            'presence': ActionPresenceSerializer,  # 'присутствие. Сервисное сообщение для извещения сервера о присутствии клиента online',
            'prоbe': None,  # 'проверка присутствия. Сервисное сообщение от сервера для проверки присутствии клиента online',
            'msg': ActionMessageSerializer,  # 'простое сообщение пользователю или в чат',
            'quit': ActionExitSerializer,  # 'отключение от сервера',
            'authenticate': None,  # 'авторизация на сервере',
            'join': None,  # 'присоединиться к чату',
            'leave': None,  # 'покинуть чат',
            ActionGetContacts.get_action(): ActionGetContactsSerializer,  # получение списка контактов
            ActionAddContact.get_action(): ActionAddDelContactSerializer,  # добавление контакта
            ActionDeleteContact.get_action(): ActionAddDelContactSerializer  # yдаление контакта
        },
        MessageSerializer.response: {
            '200': ResponseSerializer,
            '202': ResponseSerializer,
            '400': ResponseSerializer,
        },
    }

    @staticmethod
    def get_action_serializer(action):
        if action:
            res = MessageSerializerFactory.methods[MessageSerializer.action].get(str(action))
            if res:
                return res()
        raise JIMNotImplementedError

    @staticmethod
    def get_response_serializer(response):
        if response:
            res = MessageSerializerFactory.methods[MessageSerializer.response].get(str(response))
            if res:
                return res()
        raise JIMNotImplementedError

    # def __init__(self):
    #     self._serializers = dict()

    # def register_serializer_for_action(self, action, serializer):
    #     self._serializers['action'][action] = serializer

    # def register_serializer_for_(self, , serializer):
    #     self._serializers['action'][action] = serializer


class JIMSerializer():
    def __init__(self) -> None:
        self._encoding = MESSAGE_ENCODING

    def _decode_message(self, message: bytes) -> dict:
        try:

            msg = json.loads(message.decode(self._encoding))
            return msg
        except Exception as e:
            raise JIMSerializerError(e)

    def decode_action(self, message: bytes) -> Action:
        msg = self._decode_message(message)
        action = msg.get(MessageSerializer.action)
        return MessageSerializerFactory.get_action_serializer(action).from_dict(msg)

    def decode_response(self, message: bytes) -> Response:
        msg = self._decode_message(message)
        response = msg.get(MessageSerializer.response)
        return MessageSerializerFactory.get_response_serializer(response).from_dict(msg)

    def _encode_message(self, message: dict) -> bytes:
        try:
            return json.dumps(message).encode(self._encoding)
        except Exception as e:
            raise JIMSerializerError(e)

    def encode_action(self, message: Action) -> bytes:
        try:
            serializer = MessageSerializerFactory.get_action_serializer(message.action)
            msg_dict = serializer.to_dict(message)
            return self._encode_message(msg_dict)
        except Exception as e:
            raise JIMSerializerError(e)

    def encode_response(self, message: Response) -> bytes:
        try:
            serializer = MessageSerializerFactory.get_response_serializer(message.response)
            msg_dict = serializer.to_dict(message)
            return self._encode_message(msg_dict)
        except Exception as e:
            raise JIMSerializerError(e)
