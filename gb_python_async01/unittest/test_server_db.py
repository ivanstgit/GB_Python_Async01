import unittest
from config import BaseConfig
from gb_python_async01.server.db.view import ServerStorage
from gb_python_async01.common.model.user import User as CommonUser


class TestServerDB(unittest.TestCase):
    test_user = 'test1'
    config = BaseConfig

    def test_user_login_logout_OK(self):

        self.db = ServerStorage(self.config.SERVER_DB_URL)
        self.db.init_db_tables()
        user_in = CommonUser(self.test_user, status='i am here')

        self.db.user_login(user_in.username, '192.168.0.1', 2344, user_in.status)
        user = self.db.user_get(self.test_user)
        self.assertIsNotNone(user)
        if user:
            self.assertEqual(user.username, user_in.username)
            self.assertEqual(user.status, user_in.status)
            self.assertEqual(user.is_active, True)
            self.assertIsNotNone(user.last_login)

        self.db.user_logout(user_in.username)
        user = self.db.user_get(self.test_user)
        self.assertIsNotNone(user)
        if user:
            self.assertEqual(user.is_active, False)
