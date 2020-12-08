import unittest
from app import app, register_api, login_api
from register import getError

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

    def test_passwordlength(self):
        # given password is too short
        response = self.client.post("/register-result", data={
            "email": "shuyiz666@gmail.com",
            "firstname": "Shuyi",
            "lastname": "Zheng",
            "password2": "Zsy123!",
            "password3": "Zsy123!"
        })
        data = getError()
        # successful test case:expected length error while given password is too short
        self.assertEqual('Password should have length between 8~20', data)

    def test_passwordmatch(self):
        # given password and confirm password are not match
        response = self.client.post("/register-result", data={
            "email": "shuyiz666@gmail.com",
            "firstname": "Shuyi",
            "lastname": "Zheng",
            "password2": "Zsy111111!",
            "password3": "Zsy222222!"
        })
        data = getError()
        # successful test case: expected not match error while password and confirmed password are not matched

        self.assertEqual('Password and confirm password must be same. Please try again!', data)

    def test_registeredemail(self):
        # given account has already been registered
        response = self.client.post("/register-result", data={
            "email": "shuyiz@bu.edu",
            "firstname": "Shuyi",
            "lastname": "Zheng",
            "password2": "Zsy111111!",
            "password3": "Zsy111111!"
        })
        data = getError()
        # successful test case: expected has been registered error while given account has been registered
        self.assertEqual("This Email account has been registered, please try another!", data)

if __name__ == '__main__':
    unittest.main()
