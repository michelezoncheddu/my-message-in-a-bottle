import json
import unittest

from bs4 import BeautifulSoup as bs

from monolith.app import app
from monolith.forms import UserForm


class Test(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False

    
    def test_mailbox_without_login(self):
        # Test with user not logged in.
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

        # Parse HTML and get list of sent/received messages.
        parsed = bs(reply.data, 'html.parser')
        parent = parsed.find('body').find('ul')
        messages = parent.find_all('li')

        # Check number of messages.
        assert(len(messages) == 3)

        # Check content of the messages.
        for i, message in enumerate(messages):
           assert(message.text.strip() == f'{i+1} message from 1 to 1 n.{i+1} 1 1')
