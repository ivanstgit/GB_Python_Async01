import socket
import unittest

from gb_python_async01.client import *
from gb_python_async01.common.serializers import ProtocolJIM as prot


class TestClient(unittest.TestCase):

    def test_generate_presence(self):
        test_presence1 = {
            prot.action: 'presence',
            prot.time: time.time(),
            prot.user: {
                prot.user_account: 'guest'
            }
        }
        test_presence2 = generate_presence()
        test_presence2[prot.time] = test_presence1[prot.time]
        self.assertEquals(test_presence1, test_presence2)

    def test_process_response_OK(self):
        self.assertEqual(process_response({prot.response: 200}), 200)

    def test_process_response_error(self):
        self.assertEqual(process_response({prot.response: 400, prot.error: 'error'}), '400: error')
