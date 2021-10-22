import json
import unittest
import datetime

from monolith.app import app
from monolith.forms import UserForm


class Test(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False

    def test_users(self):
        pass

    #sign_up
    def test_sign_up(self):
        tested_app = app.test_client()

        test_user = {
            'email': 'test@tet.com',
            'firstname': 'testname',
            'lastname': 'testlastname',
            'password': 'testpassword',
            'dateofbirth': '9/10/2020'
        }

        reply = tested_app.post('/create_user',
                    data=json.dumps(test_user),
                    content_type='application/json', follow_redirects=True)
        
        self.assertEqual(reply.status_code, 200)
    
      

    #login
    def test_login(self):
        pass
    
    
    #logout
    def test_logout(self):
        pass


    # write a message
    def test_write_message(self):
        pass
