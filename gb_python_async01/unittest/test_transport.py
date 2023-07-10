"""Тесты модулей, используемых при клиент/серверном взаимодействии (пакета transport)"""
import unittest

from gb_python_async01.transport.errors import *
from gb_python_async01.transport.model.message import *
from gb_python_async01.transport.protocol import JIMSerializer


from gb_python_async01.transport.security import ClientSecurity, ServerSecurity
from gb_python_async01.utils.security import PasswordHash


class TestTransportSecurity(unittest.TestCase):
    """Тестирование аутентификации и шифрования"""

    test_user = "unittest_user1"
    test_password = "unittest1_contact1"

    test_message = "tefvrejo ev eojo[ f4 3] высасывс".encode()

    def test_security(self):
        """Проверить аутентификацию и шифрование"""
        client = ClientSecurity("test.key", "secret_key")

        with self.assertRaises(TransportSecurityNoSessionKeyError):
            client.decrypt_message(self.test_message)
        with self.assertRaises((TransportSecurityNoSessionKeyError)):
            client.encrypt_message(self.test_message)

        step1 = client.process_auth_step1()

        with self.assertRaises((TransportSecurityNoSessionKeyError)):
            client.decrypt_message(self.test_message)
        with self.assertRaises((TransportSecurityNoSessionKeyError)):
            client.encrypt_message(self.test_message)

        server = ServerSecurity(step1)

        step2 = server.process_auth_step2()

        step3 = client.process_auth_step3(step2, self.test_user, self.test_password)

        msg = client.encrypt_message(self.test_message)
        self.assertEqual(server.decrypt_message(msg), self.test_message)

        msg = server.encrypt_message(self.test_message)
        self.assertEqual(client.decrypt_message(msg), self.test_message)
        with self.assertRaises(TransportSecurityValidationError):
            client.decrypt_message(self.test_message)

        pass_hash = PasswordHash.generate_password_hash(
            self.test_user, self.test_password
        )
        with self.assertRaises(TransportSecurityAuthError):
            server.process_auth_step4(step3, "gigi")

        server.process_auth_step4(step3, pass_hash)

        msg_e2e_1 = "dfdsfdsfv упамукму 123"
        msg_e2e_2 = client.decrypt_e2e(client.encrypt_e2e(msg_e2e_1, client.pubkey))
        self.assertEqual(msg_e2e_1, msg_e2e_2)


class TestTransportSerializers(unittest.TestCase):
    """Тестирование протокола"""

    test_time = 65.5
    test_presence_200 = JIMActionPresence(test_time, "ua", "us")
    test_message_200 = JIMActionMessage(
        time=test_time, receiver="ua", sender="ua", message="test 1"
    )

    test_response_200 = JIMResponse200()

    test_response_400 = JIMResponse400()
    jim = JIMSerializer()

    def test_action_decode_encode_ok(self):
        """Тест успешной сериализации запроса"""
        for msg in (self.test_presence_200, self.test_message_200):
            msg_ = self.jim.decode_action(self.jim.encode_action(msg))
            self.assertEqual(msg_.__dict__, msg.__dict__)

    def test_response_decode_encode_ok(self):
        """Тест успешной сериализации ответа"""
        for msg in (self.test_response_200, self.test_response_400):
            msg_ = self.jim.decode_response(self.jim.encode_response(msg))
            self.assertEqual(msg_.__dict__, msg.__dict__)

    def test_raises(self):
        """Тест ошибок сериализации"""
        for msg in (self.test_response_200, self.test_response_400):
            msg_ = self.jim.encode_response(msg)
            with self.assertRaises((JIMError)):
                msg_ = self.jim.decode_action(msg_)  # type: ignore

        for msg in (self.test_presence_200, self.test_message_200):
            msg_ = self.jim.encode_action(msg)
            with self.assertRaises((JIMError)):
                msg_ = self.jim.decode_response(msg_)  # type: ignore
