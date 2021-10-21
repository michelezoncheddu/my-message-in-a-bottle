import json
import unittest
import datetime

from monolith.app import app
from monolith.forms import UserForm


class Test(unittest.TestCase):

    def test_users(self):
        pass

    #sign_up
    def test_sign_up(self):
        tested_app = app.test_client()

        test_user = {
            'email': 'test@test.com',
            'firstname': 'testname',
            'lastname': 'testlastname',
            'password': 'testpassword',
            'dateofbirth': '9/10/2020'
        }

        reply = tested_app.post('/create_user',
                    data=json.dumps(test_user),
                    content_type='application/json')

        print(reply)

        # body = json.loads(str(reply.data, 'utf8'))
        # self.assertEqual(body['party_number'], 0)
        # reply = tested_app.get("/create_user").get_json()
      

    #login
    def test_login(self):
        pass
    
    
    #logout
    def test_logout(self):
        pass


    # write a message
    def test_write_message(self):
        pass
