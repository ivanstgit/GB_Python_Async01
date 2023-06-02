import datetime
import socket
import unittest

from gb_python_async01.common.serializers import JIMSerializerError, decode_message, encode_message
from gb_python_async01.common.serializers import ProtocolJIM as prot


class TestSocketSerializers(unittest.TestCase):
    test_time = 65.5
    test_request_200 = {
        prot.action: 'presence',
        prot.time: test_time,
        prot.user: {
            prot.user_account: 'guest'
        }

    }

    test_response_200 = {
        prot.response: 200,
        prot.time: test_time
    }

    test_response_400 = {
        prot.response: 400,
        prot.time: test_time,
        prot.error: 'Bad Request'
    }

    def test_decode_encode_OK(self):
        for msg in (self.test_request_200, self.test_response_200, self.test_response_400):
            self.assertEqual(decode_message(encode_message(msg)), msg)

    def test_encode_message(self):
        self.assertIsInstance(encode_message(self.test_request_200), bytes)
        with self.assertRaises(JIMSerializerError):
            encode_message(datetime.datetime.now())

    def test_decode_message(self):
        with self.assertRaises(JIMSerializerError):
            decode_message(self.test_response_200)
