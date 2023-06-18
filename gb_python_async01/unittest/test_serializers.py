import datetime
import socket
import unittest

from gb_python_async01.common.JIM import *


class TestSocketSerializers(unittest.TestCase):
    test_time = 65.5
    test_presence_200 = ActionPresence(test_time, 'ua', 'us')
    test_message_200 = ActionMessage(time=test_time, receiver='ua', sender='ua', message='test 1')

    test_response_200 = Response200()

    test_response_400 = Response400()
    jim = JIMSerializer()

    def test_action_decode_encode_OK(self):
        for msg in (self.test_presence_200, self.test_message_200):
            msg_ = self.jim.decode_action(self.jim.encode_action(msg))
            self.assertEqual(msg_.__dict__, msg.__dict__)

    def test_response_decode_encode_OK(self):
        for msg in (self.test_response_200, self.test_response_400):
            msg_ = self.jim.decode_response(self.jim.encode_response(msg))
            self.assertEqual(msg_.__dict__, msg.__dict__)

    def test_raises(self):
        for msg in (self.test_response_200, self.test_response_400):
            msg_ = self.jim.encode_response(msg)
            with self.assertRaises((JIMSerializerError, JIMValidationError, JIMNotImplementedError)):
                msg_ = self.jim.decode_action(msg_)  # type: ignore

        for msg in (self.test_presence_200, self.test_message_200):
            msg_ = self.jim.encode_action(msg)
            with self.assertRaises((JIMSerializerError, JIMValidationError, JIMNotImplementedError)):
                msg_ = self.jim.decode_response(msg_)  # type: ignore
