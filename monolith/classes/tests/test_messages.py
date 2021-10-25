import json
import unittest
import datetime

from monolith.app import app
from monolith.forms import UserForm


class Test(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False

  
    
    def test_mailbox_without_login(self):
        pass
        tested_app = app.test_client()
        reply = tested_app.get('/mailbox')
        self.assertEqual(reply.status_code, 401)

        user = {
            'email': 'example@example.com',
            'password': 'admin',
        }

        tested_app.post('/login', data=json.dumps(user),content_type='application/json')
        reply = tested_app.get('/mailbox')
        self.assertEqual(reply.status_code, 200)
