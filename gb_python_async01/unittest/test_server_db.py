# import unittest
# from config import BaseConfig
# from gb_python_async01.server.db.config import ServerStorage
# from gb_python_async01.transport.model.user import User as CommonUser


# class TestServerDB(unittest.TestCase):
#     test_user = 'unittest_user1'
#     test_contact = 'unittest1_contact1'
#     config = BaseConfig

#     def test_user_login_logout_OK(self):

#         self.db = ServerStorage(self.config.SERVER_DB_URL)
#         self.db.adm_init_db_tables()
#         user_in = CommonUser(self.test_user, status='i am here')

#         self.db.cl_user_login(user_in.username, '192.168.0.1', 2344, user_in.status)
#         # user = self.db.user_get(self.test_user)
#         # self.assertIsNotNone(user)
#         # if user:
#         #     self.assertEqual(user.username, user_in.username)
#         #     self.assertEqual(user.status, user_in.status)
#         #     self.assertEqual(user.is_active, True)
#         #     self.assertIsNotNone(user.last_login)

#         # self.db.cl_user_logout(user_in.username)
#         # user = self.db.user_get(self.test_user)
#         # self.assertIsNotNone(user)
#         # if user:
#         #     self.assertEqual(user.is_active, False)

#     def test_user_contact_OK(self):

#         self.db = ServerStorage(self.config.SERVER_DB_URL)
#         self.db.adm_init_db_tables()
#         user = self.db.user_add(self.test_user)
#         contact = self.db.user_add(self.test_contact)

#         user_contact = self.db.cl_user_contact_add(self.test_user, self.test_contact)
#         user_contacts = self.db.cl_user_contact_get_list(self.test_user)
#         self.assertTrue(len(user_contacts) == 1)

#         self.db.cl_user_contact_delete(self.test_user, self.test_contact)
#         user_contact = self.db.cl_user_contact_get_list(self.test_user)
#         self.assertListEqual(user_contact, [])
