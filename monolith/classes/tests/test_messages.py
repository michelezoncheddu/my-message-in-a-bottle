import json
import unittest

from bs4 import BeautifulSoup as bs

from monolith.app import app


class Test(unittest.TestCase):

    def __init__(self, *args, **kw):
        super(Test, self).__init__(*args, **kw)

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

        reply = tested_app.post('/login', data=json.dumps(self.sender), content_type='application/json')
        self.assertEqual(reply.status_code, 302)
        
        # Unexistent message.
        reply = tested_app.get('/message/0')
        self.assertEqual(reply.status_code, 404)

        # Existent message of other users.
        reply = tested_app.get('/message/4')
        self.assertEqual(reply.status_code, 404)

        # Existent message.
        reply = tested_app.get('/message/1')
        self.assertEqual(reply.status_code, 200)

        # Delete message.
        #reply = tested_app.delete('/message/1')
        #self.assertEqual(reply.status_code, 200)

        # Delete unexistent message.
        #reply = tested_app.delete('/message/1')
        #self.assertEqual(reply.status_code, 401)

        # Delete message of other users.
        reply = tested_app.delete('/message/4')
        self.assertEqual(reply.status_code, 404)

        reply = tested_app.get('/mailbox')

        # Parse HTML and get list of sent messages.
        parsed = bs(reply.data, 'html.parser')
        parent = parsed.find(id='sent').find('ul')
        sent_messages = parent.find_all('li')
        assert(len(sent_messages) == 1)

        # Forward message
        reply = tested_app.get('/forward/1')
        self.assertEqual(reply.status_code, 302)

        
