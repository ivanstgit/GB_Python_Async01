"""Протокол передачи сообщений (JIM)"""
import json

from gb_python_async01.transport.errors import *
from gb_python_async01.transport.model.message import (
    JIMAction,
    JIMActionAddContact,
    JIMActionDeleteContact,
    JIMActionExit,
    JIMActionGetContacts,
    JIMActionMessage,
    JIMActionPresence,
    JIMAuth,
    JIMMessage,
    JIMResponse,
)
from gb_python_async01.transport.serializers.message import (
    JIMActionAddDelContactSerializer,
    JIMActionGetContactsSerializer,
    JIMActionMessageSerializer,
    JIMAuthSerializer,
    JIMActionPresenceSerializer,
    JIMActionExitSerializer,
    JIMMessageSerializer,
    JIMResponseSerializer,
)

MESSAGE_ENCODING = "utf-8"


class JIMMessageSerializerFactory:
    """Фабрика сериализаторов"""

    methods = {
        JIMAuth.get_type(): JIMAuthSerializer,
        JIMAction.get_type(): {
            JIMActionPresence.get_action(): JIMActionPresenceSerializer,  # 'присутствие. Сервисное сообщение для извещения сервера о присутствии клиента online',
            "prоbe": None,  # 'проверка присутствия. Сервисное сообщение от сервера для проверки присутствии клиента online',
            JIMActionMessage.get_action(): JIMActionMessageSerializer,  # 'простое сообщение пользователю или в чат',
            JIMActionExit.get_action(): JIMActionExitSerializer,  # 'отключение от сервера',
            "authenticate": None,  # 'авторизация на сервере',
            "join": None,  # 'присоединиться к чату',
            "leave": None,  # 'покинуть чат',
            JIMActionGetContacts.get_action(): JIMActionGetContactsSerializer,  # получение списка контактов
            JIMActionAddContact.get_action(): JIMActionAddDelContactSerializer,  # добавление контакта
            JIMActionDeleteContact.get_action(): JIMActionAddDelContactSerializer,  # yдаление контакта
        },
        JIMResponse.get_type(): JIMResponseSerializer,
    }

    @staticmethod
    def get_auth_serializer():
        res = JIMMessageSerializerFactory.methods[JIMAuth.get_type()]
        if res:
            return res()
        raise JIMNotImplementedError

    @staticmethod
    def get_action_serializer(action):
        if action:
            res = JIMMessageSerializerFactory.methods[JIMAction.get_type()].get(
                str(action)
            )
            if res:
                return res()
        raise JIMNotImplementedError

    @staticmethod
    def get_response_serializer(response):
        if response:
            res = JIMMessageSerializerFactory.methods[JIMResponse.get_type()]
            if res:
                return res()
        raise JIMNotImplementedError


class JIMSerializer:
    """Сериализаторы сообщений"""

    def __init__(self) -> None:
        self._encoding = MESSAGE_ENCODING

    def _decode_message(self, message: bytes) -> dict:
        try:
            msg = json.loads(message.decode(self._encoding))
            return msg
        except Exception as exc:
            raise JIMSerializerError from exc

    def from_bytes(self, message: bytes) -> JIMMessage:
        """Сериализовать байтовую строку в сообщение"""
        msg = self._decode_message(message)
        action = msg.get(JIMMessageSerializer.action)
        response = msg.get(JIMMessageSerializer.response)
        if action and not response:
            return JIMMessageSerializerFactory.get_action_serializer(action).from_dict(
                msg
            )
        elif response and not action:
            return JIMMessageSerializerFactory.get_response_serializer(
                response
            ).from_dict(msg)
        else:
            return JIMMessageSerializerFactory.get_auth_serializer().from_dict(msg)

    def decode_auth(self, message: bytes) -> JIMAuth:
        """Сериализовать сообщение аутентификации из байтовой строки"""
        msg = self._decode_message(message)
        return JIMMessageSerializerFactory.get_auth_serializer().from_dict(msg)

    def decode_action(self, message: bytes) -> JIMAction:
        """Сериализовать запрос из байтовой строки"""
        msg = self._decode_message(message)
        action = msg.get(JIMMessageSerializer.action)
        return JIMMessageSerializerFactory.get_action_serializer(action).from_dict(msg)

    def decode_response(self, message: bytes) -> JIMResponse:
        """Сериализовать ответ из байтовой строки"""
        msg = self._decode_message(message)
        response = msg.get(JIMMessageSerializer.response)
        return JIMMessageSerializerFactory.get_response_serializer(response).from_dict(
            msg
        )

    def _encode_message(self, message: dict) -> bytes:
        try:
            return json.dumps(message).encode(self._encoding)
        except Exception as exc:
            raise JIMSerializerError from exc

    def to_bytes(self, message: JIMMessage) -> bytes:
        """Сериализовать сообщение в байтовую строку"""
        try:
            if message.msg_type == JIMAuth.get_type():
                serializer = JIMMessageSerializerFactory.get_auth_serializer()
            elif message.msg_type == JIMAction.get_type():
                serializer = JIMMessageSerializerFactory.get_action_serializer(message.action)  # type: ignore
            elif message.msg_type == JIMResponse.get_type():
                serializer = JIMMessageSerializerFactory.get_response_serializer(
                    message
                )
            else:
                raise JIMSerializerError

            msg_dict = serializer.to_dict(message)
            return self._encode_message(msg_dict)
        except Exception as exc:
            raise JIMSerializerError from exc

    def encode_auth(self, message: JIMAuth) -> bytes:
        """Сериализовать сообщение аутентификации в байтовоую строку"""
        try:
            serializer = JIMMessageSerializerFactory.get_auth_serializer()
            msg_dict = serializer.to_dict(message)
            return self._encode_message(msg_dict)
        except Exception as exc:
            raise JIMSerializerError from exc

    def encode_action(self, message: JIMAction) -> bytes:
        """Сериализовать запрос в байтовоую строку"""
        try:
            serializer = JIMMessageSerializerFactory.get_action_serializer(
                message.action
            )
            msg_dict = serializer.to_dict(message)
            return self._encode_message(msg_dict)
        except Exception as exc:
            raise JIMSerializerError from exc

    def encode_response(self, message: JIMResponse) -> bytes:
        """Сериализовать ответ в байтовоую строку"""
        try:
            serializer = JIMMessageSerializerFactory.get_response_serializer(
                message.response
            )
            msg_dict = serializer.to_dict(message)
            return self._encode_message(msg_dict)
        except Exception as exc:
            raise JIMSerializerError from exc
