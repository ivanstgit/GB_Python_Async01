import socket
import unittest

from gb_python_async01.server import *
from gb_python_async01.serializers import ProtocolJIM as prot


class TestServer(unittest.TestCase):
    test_time = 65.5
    test_request_200 = {
        prot.action: 'presence',
        prot.time: time.time(),
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

    def test_process_request_OK(self):
        test_response = process_request(self.test_request_200)
        test_response[prot.time] = self.test_time
        self.assertEqual(test_response, self.test_response_200)

    def test_process_request_no_action(self):
        test_request = self.test_request_200.copy()
        test_request.pop(prot.action)
        test_response = process_request(test_request)
        test_response[prot.time] = self.test_time
        self.assertEqual(test_response, self.test_response_400)

    def test_process_request_incorrect_action(self):
        test_request = self.test_request_200.copy()
        test_request[prot.action] = '...```'
        test_response = process_request(test_request)
        test_response[prot.time] = self.test_time
        self.assertEqual(test_response, self.test_response_400)

    def test_process_request_no_time(self):
        test_request = self.test_request_200.copy()
        test_request.pop(prot.time)
        test_response = process_request(test_request)
        test_response[prot.time] = self.test_time
        self.assertEqual(test_response, self.test_response_400)

    def test_process_request_no_user(self):
        test_request = self.test_request_200.copy()
        test_request.pop(prot.user)
        test_response = process_request(test_request)
        test_response[prot.time] = self.test_time
        self.assertEqual(test_response, self.test_response_400)
