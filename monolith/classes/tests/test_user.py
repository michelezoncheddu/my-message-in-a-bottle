import os
import json
import unittest

from bs4 import BeautifulSoup as bs
from werkzeug.utils import redirect

from monolith.app import app

from monolith.forms import UserForm


class Test(unittest.TestCase):

    def __init__(self, *args, **kw):
        super(Test, self).__init__(*args, **kw)
        self.user = {
            'email': 'example@example.com',
            'password': 'admin'
        }


    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False

    # /profile tests
    def test_profile(self):
        tested_app = app.test_client()

        # profile without login
        reply = tested_app.get('/profile')
        self.assertEqual(reply.status_code, 401)

        # login
        reply = tested_app.post('/login', data=json.dumps(self.user), content_type='application/json')
        self.assertEqual(reply.status_code, 302)

        # profile with login
        reply = tested_app.get('/profile')
        self.assertEqual(reply.status_code, 200)

        # change profile pic : no selected file
        data = {'dir': '/profile', 'submit': 'Upload'}
        reply = tested_app.post('/profile', data=data)
        self.assertEqual(reply.status_code, 400)

        # change profile pic : invalid format
        filename = os.path.join(os.path.dirname('monolith/static/profile/'), 'test_invalid_format.txt')
        data = {'dir': '/profile',
                'submit': 'Upload',
                'file': (open(filename, 'rb'), filename)
                }
        reply = tested_app.post('/profile', data=data)
        self.assertEqual(reply.status_code, 400)

        # change profile pic
        filename = os.path.join(os.path.dirname('monolith/static/profile/'), 'default.png')
        data = {'dir': '/profile',
                'submit': 'Upload',
                'file': (open(filename, 'rb'), filename)
                }
        reply = tested_app.post('/profile', data=data)
        self.assertEqual(reply.status_code, 200)


    # /unregister tests
    def test_unregister(self):
        tested_app = app.test_client()

        # unregister without login
        reply = tested_app.get('/unregister')
        self.assertEqual(reply.status_code, 401)

        # login
        reply = tested_app.post('/login', data=json.dumps(self.user), content_type='application/json')
        self.assertEqual(reply.status_code, 302)

        # unregister with login
        reply = tested_app.get('/unregister')
        self.assertEqual(reply.status_code, 200)

        # try unregister with wrong password
        data = {'dir': '/unregister',
                'submit': 'Confirm', 
                'password': 'incorrectpw'}
        reply = tested_app.post('/unregister', data=data)
        self.assertEqual(reply.status_code, 400)

        """create dummy user for unregister
        # logout
        reply = tested_app.get('/logout')
        self.assertEqual(reply.status_code, 302)
        # signup
        data = {'dir': '/create_user',
                'submit': 'Submit'
        }
        reply = tested_app.post('/create_user', data=data)
        self.assertEqual(reply.status_code, 302)
        # login
        data = {'dir': '/login',
                'submit': 'Publish',
                'email': 'todelete@todelete.it',
                'password': 'pwdummy'}
        reply = tested_app.post('/createform', data=data)
        self.assertEqual(reply.status_code, 200)"""
        # unregister 
        data = {'dir': '/unregister',
                'submit': 'Confirm', 
                'password': 'admin'}
        reply = tested_app.post('/unregister', data=data)
        self.assertEqual(reply.status_code, 302)