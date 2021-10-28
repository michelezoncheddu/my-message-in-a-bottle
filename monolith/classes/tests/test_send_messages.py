import json
from typing import Text
import unittest
import flask

from bs4 import BeautifulSoup as bs
from werkzeug import test

from monolith.app import app


class Test(unittest.TestCase):

    def __init__(self, *args, **kw):
        super(Test, self).__init__(*args, **kw)

        self.sender = {
            'email': 's@s',
            'password': 'sender'
        }

        self.message = {
            'text_area': 'text',
            'delivery_date': '31/12/2022'
        }


    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.secret_key = 'ANOTHER ONE'

    def test_message(self):
        tested_app = app.test_client()

        # Create message
        # Check GET create_message
        reply = tested_app.get('/create_message')
        # Test with user not logged in.
        self.assertEqual(reply.status_code, 401)
        # Login with the user
        tested_app.post('/login', data=json.dumps(self.sender), content_type='application/json')
        reply = tested_app.get('/create_message')
        self.assertEqual(reply.status_code, 200)
        # Check if the html returned page is the create message page
        self.assertIn(b'Insert message text', reply.data)

        # Check POST create_message
        #reply = tested_app.post('/create_message', data=json.dumps(self.message), content_type='application/json')
        #self.assertEqual(reply.status_code, 200)

        
        
        



