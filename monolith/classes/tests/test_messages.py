import json
import unittest

from bs4 import BeautifulSoup as bs

from monolith.app import app

from ...database import Message
from ...views.messages import filter_language

class Test(unittest.TestCase):

    def __init__(self, *args, **kw):
        super(Test, self).__init__(*args, **kw)

        self.admin = {
            'email': 'admin@test.com',
            'password': 'Admin1@'
        }

        self.sender = {
            'email': 's@test.com',
            'password': 'Sender1@'
        }

        self.recipient = {
            'email': 'r@test.com',
            'password': 'Recipient1@'
        }
        


    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False

    
    def test_mailbox(self):
        tested_app = app.test_client()

        # Test with user not logged in.
        reply = tested_app.get('/mailbox')
        self.assertEqual(reply.status_code, 401)

        reply = tested_app.post('/login', data=json.dumps(self.sender), content_type='application/json')
        self.assertEqual(reply.status_code, 302)
        
        reply = tested_app.get('/mailbox')

        # Parse HTML and get list of sent messages.
        parsed = bs(reply.data, 'html.parser')
        parent = parsed.find(id='sent').find('ul')
        sent_messages = parent.find_all('li')
        assert(len(sent_messages) == 1)

        # Get list of received messages.
        parent = parsed.find(id='received').find('ul')
        received_messages = parent.find_all('li')
        assert(len(received_messages) == 0)

        # Check content of the messages.
        #for i, message in enumerate(sent_messages):
        #   assert(message.text.strip() == f'{i+1} message from 1 to 1 n.{i+1} 1 1')

    def test_message(self):
        tested_app = app.test_client()
    
        # Test without login.
        reply = tested_app.get('/message/1')
        self.assertEqual(reply.status_code, 401)
        
        reply = tested_app.post('/login', data=json.dumps(self.recipient), content_type='application/json')
        self.assertEqual(reply.status_code, 302)

        # Existent message of other users.
        reply = tested_app.get('/message/1')
        self.assertEqual(reply.status_code, 200)
        
        tested_app = app.test_client()
    

        reply = tested_app.post('/login', data=json.dumps(self.sender), content_type='application/json')
        self.assertEqual(reply.status_code, 302)
        
        # Unexistent message.
        reply = tested_app.get('/message/0')
        self.assertEqual(reply.status_code, 404)

        # Existent message.
        reply = tested_app.get('/message/1')
        self.assertEqual(reply.status_code, 200)

        reply = tested_app.get('/mailbox')
        # Parse HTML and get list of sent messages.
        parsed = bs(reply.data, 'html.parser')
        parent = parsed.find(id='sent').find('ul')
        sent_messages = parent.find_all('li')
        assert(len(sent_messages) == 1)

        # Edit an alredy sent message
        reply = tested_app.get('/create_message?draft_id=1')
        self.assertEqual(reply.status_code, 403)

        # Edit a draft
        reply = tested_app.get('/create_message?draft_id=2')
        self.assertEqual(reply.status_code, 200)

        # Forward a draft
        reply = tested_app.get('/create_message?forw_id=2')
        self.assertEqual(reply.status_code, 403)

        # Reply to a draft
        reply = tested_app.get('/create_message?reply_id=2')
        self.assertEqual(reply.status_code, 403)
        
        # Forward message
        reply = tested_app.get('/create_message?forw_id=1')
        self.assertEqual(reply.status_code, 200)

        # Reply message
        reply = tested_app.get('/create_message?reply_id=1')
        self.assertEqual(reply.status_code, 200)

        # Delete message.
        reply = tested_app.delete('/message/1')
        self.assertEqual(reply.status_code, 200)

        # Delete unexistent message.
        reply = tested_app.delete('/message/1')
        self.assertEqual(reply.status_code, 403)

        # Delete message of other users.
        reply = tested_app.delete('/message/4')
        self.assertEqual(reply.status_code, 404)

        reply = tested_app.post('/login', data=json.dumps(self.admin), content_type='application/json')
        self.assertEqual(reply.status_code, 302)

        # Delete message of other users.
        reply = tested_app.delete('/message/1')
        self.assertEqual(reply.status_code, 200)

        # Check bad language message
        tocensor_message = Message()
        Message.recipient_id = '1'
        Message.delivery_date = '10/10/2022'
        Message.text = 'Asshole'
        self.assertEqual({'recipient_id': '1', 'delivery_date': '10/10/2022', 'text': '****'}, filter_language(tocensor_message))

    def test_message_post(self): 
        tested_app = app.test_client()
        
        #Message test vector SAVE
        self.message = {
            'text_area': 'text',
            'delivery_date': '2022-10-10T08:00',
            'save_button':'Save'
        }

        # Check POST create_message SAVE
        tested_app.post('/login', data=json.dumps(self.sender), content_type='application/json')
        reply = tested_app.post('/create_message', data=json.dumps(self.message), content_type='application/json')
        self.assertEqual(reply.status_code, 302)

        #Message test vector SAVE+HIDDEN
        self.message = {
            'message_id_hidden':1,
            'text_area': 'text',
            'delivery_date': '2022-10-10T08:00',
            'save_button':'Save'
        }

        # Check POST create_message SAVE+HIDDEN
        tested_app.post('/login', data=json.dumps(self.sender), content_type='application/json')
        reply = tested_app.post('/create_message', data=json.dumps(self.message), content_type='application/json')
        self.assertEqual(reply.status_code, 302)

        #Message test vector SEND
        self.message = {
            'text_area': 'text',
            'delivery_date': '2022-10-10T08:00',
            'users_list':'1',
            'send_button':'Send'
        }

        # Check POST create_message SEND
        tested_app.post('/login', data=json.dumps(self.sender), content_type='application/json')
        reply = tested_app.post('/create_message', data=json.dumps(self.message), content_type='application/json')
        self.assertEqual(reply.status_code, 302)

        #Message test vector SEND+HIDDEN
        self.message = {
            'message_id_hidden':1,
            'text_area': 'text',
            'delivery_date': '2022-10-10T08:00',
            'users_list':'1',
            'send_button':'Send'
        }

        # Check POST create_message SEND+HIDDEN
        tested_app.post('/login', data=json.dumps(self.sender), content_type='application/json')
        reply = tested_app.post('/create_message', data=json.dumps(self.message), content_type='application/json')
        self.assertEqual(reply.status_code, 302)

        #ERRORS

        #Message test vector SEND wrong date        
        self.message = {
            'text_area': 'text',
            'delivery_date': '2021-10-10T08:00',
            'users_list':'1',
            'send_button':'Send'
        }

        # Check POST create_message SEND with wrong date
        tested_app.post('/login', data=json.dumps(self.sender), content_type='application/json')
        reply = tested_app.post('/create_message', data=json.dumps(self.message), content_type='application/json')
        self.assertEqual(reply.status_code, 409)

        #Message test vector SEND without recipient
        self.message = {
            'text_area': 'text',
            'delivery_date': '2022-10-10T08:00',
            'send_button':'Send'
        }

        # Check POST create_message SEND without recipient
        tested_app.post('/login', data=json.dumps(self.sender), content_type='application/json')
        reply = tested_app.post('/create_message', data=json.dumps(self.message), content_type='application/json')
        self.assertEqual(reply.status_code, 409)
        
        #Message test vector SAVE wrong date
        self.message = {
            'text_area': 'text',
            'delivery_date': '2021-10-10T08:00',
            'save_button':'Save'
        }

        # Check POST create_message SAVE with wrong date
        tested_app.post('/login', data=json.dumps(self.sender), content_type='application/json')
        reply = tested_app.post('/create_message', data=json.dumps(self.message), content_type='application/json')
        self.assertEqual(reply.status_code, 409)


        
        



        
