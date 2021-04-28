import unittest
import os
import json

from app import *


class SignupTest(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        initialize_db()

    def test_successful_purchase(self):

        response = self.app.get('/buy/1', headers={"Content-Type": "application/json"})

        # print(response)
        self.assertEqual(200, response.status_code)

    def test_unsuccessful_purchase(self):

        response = self.app.get('/buy/3', headers={"Content-Type": "application/json"})

        # print(response)
        self.assertEqual(404, response.status_code)


    def tearDown(self):
        # Reset Database after the test is complete
        initialize_db()