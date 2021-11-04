import json
import os,io
from typing import Text
import unittest
import flask 
from bs4 import BeautifulSoup as bs
from werkzeug import test

from ...views.messages import filter_language
from ...database import Message

from monolith.app import app


class Test(unittest.TestCase):

    def __init__(self, *args, **kw):
        super(Test, self).__init__(*args, **kw)

        self.sender = {
            'email': 's@test.com',
            'password': 'Sender1@',
        }

        self.recipient = {
            'email': 'r@test.com',
            'password': 'Sender1@'
        }      


    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.secret_key = 'ANOTHER ONE'

    def test_message_get(self):
        
        tested_app = app.test_client()
        #self.draft={'draft_id':'2'}

        # Test with user not logged in.
        reply = tested_app.get('/create_message?draft_id=2')

        
        self.assertEqual(reply.status_code, 401)

        # Login with the user
        tested_app.post('/login', data=json.dumps(self.sender), content_type='application/json')

        # Create message
        # Check GET create_message
        reply = tested_app.get('/create_message')

        # Test with user not logged in.
        self.assertEqual(reply.status_code, 200)
        

        
        reply = tested_app.get('/create_message')
        
        self.assertEqual(reply.status_code, 200)
        # Check if the html returned page is the create message page
        self.assertIn(b'essage', reply.data)

        # Login with the user
        tested_app.post('/login', data=json.dumps(self.sender), content_type='application/json')

        #TODO: GET /create_message?draft_id=2
        reply = tested_app.get('/create_message?draft_id=2')
        #TODO: GET /create_message?forw_id=2
        reply = tested_app.get('/create_message?forw_id=2')
        #TODO: GET /create_message?reply_id=2
        reply = tested_app.get('/create_message?reply_id=2')


    def test_message_post(self): 
        tested_app = app.test_client()
        filename=os.path.join(os.path.dirname('monolith/static/profile/'), 'default.png')
        self.message = {
            'text_area': 'text',
            'delivery_date': '2022-10-10T08:00',
            'submit_button':'Save'
        }

        # Check POST create_message SAVE
        tested_app.post('/login', data=json.dumps(self.sender), content_type='application/json')
        reply = tested_app.post('/create_message', data=json.dumps(self.message), content_type='application/json')
        self.assertEqual(reply.status_code, 302)

        self.message = {
            'message_id_hidden':1,
            'text_area': 'text',
            'delivery_date': '2022-10-10T08:00',
            'submit_button':'Save'
        }

        # Check POST create_message SAVE+HIDDEN
        tested_app.post('/login', data=json.dumps(self.sender), content_type='application/json')
        reply = tested_app.post('/create_message', data=json.dumps(self.message), content_type='application/json')
        self.assertEqual(reply.status_code, 302)

        self.message = {
            'text_area': 'text',
            'delivery_date': '2022-10-10T08:00',
            'users_list':'1',
            'submit_button2':'Send'
        }

        # Check POST create_message SEND
        tested_app.post('/login', data=json.dumps(self.sender), content_type='application/json')
        reply = tested_app.post('/create_message', data=json.dumps(self.message), content_type='application/json')
        self.assertEqual(reply.status_code, 302)

        self.message = {
            'message_id_hidden':1,
            'text_area': 'text',
            'delivery_date': '2022-10-10T08:00',
            'users_list':'1',
            'submit_button2':'Send'
        }

        # Check POST create_message SEND+HIDDEN
        tested_app.post('/login', data=json.dumps(self.sender), content_type='application/json')
        reply = tested_app.post('/create_message', data=json.dumps(self.message), content_type='application/json')
        self.assertEqual(reply.status_code, 302)



    def test_message_read(self):
        tested_app = app.test_client()
          
        # Read message
        tested_app.post('/login', data=json.dumps(self.sender), content_type='application/json')
        reply = tested_app.get('/message/2')
        
        self.assertEqual(reply.status_code, 200)

        # Check bad language message
        tocensor_message = Message()
        Message.recipient_id = '1'
        Message.delivery_date = '10/10/2022'
        Message.text = 'Asshole'
        self.assertEqual({'recipient_id': '1', 'delivery_date': '10/10/2022', 'text': '****'}, filter_language(tocensor_message))


    def test_message_read_draft(self):
        tested_app = app.test_client()
        tested_app.post('/login', data=json.dumps(self.sender), content_type='application/json')
        reply = tested_app.get('/messages/draft')
        self.assertEqual(reply.status_code, 200)

        






        
        
        



