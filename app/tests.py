import unittest
from django.test import TestCase
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from django.contrib.auth import get_user_model
# Create your tests here.

class DashboardTest(unittest.TestCase):
    def setUp(self):
        self.client = webdriver.Chrome(ChromeDriverManager().install())
        # Test Id 세팅
        self.test_id = "admin"
        self.test_password = "qpsej0424!"

        # Test Login 세팅
        login_data = {
            "Id" : self.test_id,
            "Password" : self.test_password
        }
        login_response = self.client.post('http://ansana-dev.ap-northeast-2.elasticbeanstalk.com/api/swagger/user-management/users/login', login_data, data=login_data)

        self.token =login_response.data.get("Token")
        self.assertTrue(self.token)

    def tearDown(self):
        self.client.quit()

        

if __name__ == '__main__':
    unittest.main()

