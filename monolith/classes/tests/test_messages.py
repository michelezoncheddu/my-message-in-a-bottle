import json
import unittest

from bs4 import BeautifulSoup as bs

from monolith.app import app


class Test(unittest.TestCase):

    def __init__(self, *args, **kw):
        super(Test, self).__init__(*args, **kw)

        self.admin = {
            'email': 'admin@admin',
            'password': 'admin'
        }

        self.sender = {
            'email': 's@s',
            'password': 'sender'
        }

        self.recipient = {
            'email': 'r@r',
            'password': 'recipient'
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
        assert(len(sent_messages) == 0)

        # Get list of recieved messages.
        parent = parsed.find(id='recieved').find('ul')
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
        self.assertEqual(reply.status_code, 401)
        
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
        assert(len(sent_messages) == 0)

        # Edit an alredy sent message
        reply = tested_app.get('/create_message?draft_id=1')
        self.assertEqual(reply.status_code, 400)

        # Edit a draft
        reply = tested_app.get('/create_message?draft_id=2')
        self.assertEqual(reply.status_code, 200)

        # Forward a draft
        reply = tested_app.get('/create_message?forw_id=2')
        self.assertEqual(reply.status_code, 400)

        # Reply to a draft
        reply = tested_app.get('/create_message?reply_id=2')
        self.assertEqual(reply.status_code, 404)
        
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
        self.assertEqual(reply.status_code, 401)

        # Delete message of other users.
        reply = tested_app.delete('/message/4')
        self.assertEqual(reply.status_code, 404)

        reply = tested_app.post('/login', data=json.dumps(self.admin), content_type='application/json')
        self.assertEqual(reply.status_code, 302)

        # Delete message of other users.
        reply = tested_app.delete('/message/1')
        self.assertEqual(reply.status_code, 200)
        



        
