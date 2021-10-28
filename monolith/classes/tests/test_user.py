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

        # admin user
        self.admin = {
            'email': 'admin@admin',
            'password': 'admin'
        }
        # common user
        self.common_user = {
            'email': 's@s',
            'password': 'sender'
        }
        # dummy user for /unregister
        self.create_todelete_user = {
            'email': 'todelete@todelete',
            'firstname': 'todelete',
            'lastname': 'todelete',
            'password': 'todelete',
            'dateofbirth': '9/10/2020',
            'location': 'Pisa'
        }
        self.todelete_user = {
            'email': 'todelete@todelete',
            'password': 'todelete'
        }
        # dummy user for testing ban 1
        self.create_toban1_user = {
            'email': 'toban1@toban1',
            'firstname': 'toban1',
            'lastname': 'toban1',
            'password': 'toban1',
            'dateofbirth': '9/10/2020',
            'location': 'Pisa'
        }
        self.toban1_user = {
            'email': 'toban1@toban1',
            'password': 'toban1'
        }
        # dummy user for testing ban 1
        self.create_toban2_user = {
            'email': 'toban2@toban2',
            'firstname': 'toban2',
            'lastname': 'toban2',
            'password': 'toban2',
            'dateofbirth': '9/10/2020',
            'location': 'Pisa'
        }
        self.toban2_user = {
            'email': 'toban1@toban2',
            'password': 'toban2'
        }


    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False


    # general tests for common user
    def test_user(self):
        tested_app = app.test_client()

        # /profile without login
        reply = tested_app.get('/profile')
        self.assertEqual(reply.status_code, 401)

        # login
        reply = tested_app.post('/login', data=json.dumps(self.common_user), content_type='application/json')
        self.assertEqual(reply.status_code, 302)

        # users
        reply = tested_app.get('/users')
        self.assertEqual(reply.status_code, 200)

        # reported_users
        reply = tested_app.get('reported_users')
        self.assertEqual(reply.status_code, 401)

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


    # general tests for admin
    def test_admin(self):
        tested_app = app.test_client()

        # /profile without login
        reply = tested_app.get('/profile')
        self.assertEqual(reply.status_code, 401)

        # login
        reply = tested_app.post('/login', data=json.dumps(self.admin), content_type='application/json')
        self.assertEqual(reply.status_code, 302)

        # reported_users
        reply = tested_app.get('reported_users')
        self.assertEqual(reply.status_code, 200)

        # users
        reply = tested_app.get('/users')
        self.assertEqual(reply.status_code, 200)

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

        # get /unregister without login
        reply = tested_app.get('/unregister')
        self.assertEqual(reply.status_code, 401)

        # create todelete account
        reply = tested_app.post('/create_user',
                    data=json.dumps(self.create_todelete_user),
                    content_type='application/json', follow_redirects=True)
        
        self.assertEqual(reply.status_code, 200)

        # login
        reply = tested_app.post('/login', data=json.dumps(self.todelete_user), content_type='application/json')
        self.assertEqual(reply.status_code, 302)

        # get /unregister with login
        reply = tested_app.get('/unregister')
        self.assertEqual(reply.status_code, 200)

        # try unregister with wrong password
        data = {'dir': '/unregister',
                'submit': 'Confirm', 
                'password': 'incorrectpw'}
        reply = tested_app.post('/unregister', data=data)
        self.assertEqual(reply.status_code, 400)

        # try unregister with wrong password
        data = {'dir': '/unregister',
                'submit': 'Confirm', 
                'password': 'todelete'}
        reply = tested_app.post('/unregister', data=data)
        self.assertEqual(reply.status_code, 302)


    # report tests
    def test_report(self):
        tested_app = app.test_client()

        # login
        reply = tested_app.post('/login', data=json.dumps(self.common_user), content_type='application/json')
        self.assertEqual(reply.status_code, 302)

        # TODO: report an user


    # ban tests
    def test_report(self):
        tested_app = app.test_client()

        # login
        reply = tested_app.post('/login', data=json.dumps(self.admin), content_type='application/json')
        self.assertEqual(reply.status_code, 302)

        # TODO: ban an user