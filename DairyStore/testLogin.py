import unittest
from app import app, register_api, login_api
from login import getErrorMsg

class MyTestClass(unittest.TestCase):
    @classmethod
    def setUp(self) -> None:
        app.config.update(
            TESTING=True
        )
        self.client = app.test_client()

    def test_app_exist(self):
        self.assertIsNotNone(app)

    def test_app_is_testing(self):
        self.assertTrue(app.config['TESTING'])

    def test_empty_email(self):
        response = self.client.post('/login-result', data=dict(
            email="",
            password="Qwer1234"
        ), follow_redirects=True)
        data = getErrorMsg()
        self.assertEqual("Empty field.", data)

    def test_not_exist_email(self):
        response = self.client.post('/login-result', data=dict(
            email="test2@bu.edu",
            password="Qwer1234"
        ), follow_redirects=True)
        data = getErrorMsg()
        self.assertEqual("Email not exists. Please sign up.", data)

    def test_wrong_email_password(self):
        response = self.client.post('/login-result', data=dict(
            email="test1@bu.edu",
            password="Qwer12345"
        ), follow_redirects=True)
        data = getErrorMsg()
        self.assertEqual("Email and password not match.", data)

    def test_wrong_email_password2(self):
        response = self.client.post('/login-result', data=dict(
            email="test1@bu.edu",
            password="Qwer12345"
        ), follow_redirects=True)
        data = getErrorMsg()
        self.assertEqual("Email and password not match.", data)

if __name__ == '__main__':
    unittest.main()
