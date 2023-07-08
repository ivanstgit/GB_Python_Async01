
import unittest

from gb_python_async01.utils.errors import UtilsSecurityAuthError, UtilsSecurityNoSessionKeyError, UtilsSecurityValidationError
from gb_python_async01.utils.security import (ClientSecurity, PasswordHash,
                                              ServerSecurity)


class TestEncrtption(unittest.TestCase):
    test_user = 'unittest_user1'
    test_password = 'unittest1_contact1'

    test_message = 'tefvrejo ev eojo[ f4 3] высасывс'.encode()

    def test_auth_OK(self):
        client = ClientSecurity('test.key', 'secret_key')

        with self.assertRaises((UtilsSecurityNoSessionKeyError)):
            client.decrypt_message(self.test_message)
        with self.assertRaises((UtilsSecurityNoSessionKeyError)):
            client.encrypt_message(self.test_message)

        step1 = client.process_auth_step1()

        with self.assertRaises((UtilsSecurityNoSessionKeyError)):
            client.decrypt_message(self.test_message)
        with self.assertRaises((UtilsSecurityNoSessionKeyError)):
            client.encrypt_message(self.test_message)

        server = ServerSecurity(step1)

        step2 = server.process_auth_step2()

        step3 = client.process_auth_step3(step2, self.test_user, self.test_password)

        msg = client.encrypt_message(self.test_message)
        self.assertEqual(server.decrypt_message(msg), self.test_message)

        msg = server.encrypt_message(self.test_message)
        self.assertEqual(client.decrypt_message(msg), self.test_message)
        with self.assertRaises(UtilsSecurityValidationError):
            rr = client.decrypt_message(self.test_message)

        hash = PasswordHash.generate_password_hash(self.test_user, self.test_password)
        with self.assertRaises((UtilsSecurityAuthError)):
            server.process_auth_step4(step3, 'gigi')

        server.process_auth_step4(step3, hash)

        msg_e2e_1 = 'dfdsfdsfv упамукму 123'
        msg_e2e_2 = client.decrypt_e2e(client.encrypt_e2e(msg_e2e_1, client.pubkey))
        self.assertEqual(msg_e2e_1, msg_e2e_2)
