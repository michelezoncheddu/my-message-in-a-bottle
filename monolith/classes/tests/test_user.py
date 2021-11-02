import os
import json
import unittest
import pytest

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
            'password': 'Admin1@'
        }
        # common user
        self.common_user = {
            'email': 's@s',
            'password': 'Sender1@'
        }
        # dummy user for /unregister
        self.create_tounregister_user = {
            'email': 'tounregister@tounregister',
            'firstname': 'tounregister',
            'lastname': 'tounregister',
            'password': 'Tounregister1@',
            'dateofbirth': '9/10/2020',
            'location': 'Pisa'
        }
        self.tounregister_user = {
            'email': 'tounregister@tounregister',
            'password': 'Tounregister1@'
        }
        # dummy user for delete user
        self.create_todelete_user = {
            'email': 'todelete@todelete',
            'firstname': 'todelete',
            'lastname': 'todelete',
            'password': 'Todelete1@',
            'dateofbirth': '9/10/2020',
            'location': 'Pisa'
        }
        self.todelete_user = {
            'email': 'todelete@todelete',
            'password': 'Todelete1@'
        }
        # dummy user for testing reject reported user
        self.create_toreject_user = {
            'email': 'toreject@toreject',
            'firstname': 'toreject',
            'lastname': 'toreject',
            'password': 'Toreject1@',
            'dateofbirth': '9/10/2020',
            'location': 'Pisa'
        }
        # dummy user for testing ban 1
        self.create_toban1_user = {
            'email': 'toban1@toban1',
            'firstname': 'toban1',
            'lastname': 'toban1',
            'password': 'Toban1@',
            'dateofbirth': '9/10/2020',
            'location': 'Pisa'
        }
        self.toban1_user = {
            'email': 'toban1@toban1',
            'password': 'Toban1@'
        }
        # dummy user for testing ban 2
        self.create_toban2_user = {
            'email': 'toban2@toban2',
            'firstname': 'toban2',
            'lastname': 'toban2',
            'password': 'Toban2@',
            'dateofbirth': '9/10/2020',
            'location': 'Pisa'
        }
        self.toban2_user = {
            'email': 'toban2@toban2',
            'password': 'Toban2@'
        }


    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False


    # general tests for common user
    @pytest.mark.run(order=1)
    def test_user(self):
        tested_app = app.test_client()

        # /create_user
        reply = tested_app.get('/create_user')
        self.assertEqual(reply.status_code, 200)

        # create dummy account 1
        reply = tested_app.post('/create_user',
                    data=json.dumps(self.create_toreject_user),
                    content_type='application/json', follow_redirects=True)
        self.assertEqual(reply.status_code, 200)

        # create dummy account 2
        reply = tested_app.post('/create_user',
                    data=json.dumps(self.create_toban1_user),
                    content_type='application/json', follow_redirects=True)
        self.assertEqual(reply.status_code, 200)

        # /profile without login
        reply = tested_app.get('/profile')
        self.assertEqual(reply.status_code, 401)

        # login
        reply = tested_app.post('/login', data=json.dumps(self.common_user), content_type='application/json')
        self.assertEqual(reply.status_code, 302)

        # /profile
        reply = tested_app.get('/profile')
        self.assertEqual(reply.status_code, 200)

        # /users
        reply = tested_app.get('/users')
        self.assertEqual(reply.status_code, 200)

        # /reported_users (denied access)
        reply = tested_app.get('reported_users')
        self.assertEqual(reply.status_code, 401)

        # change profile pic : no selected file
        data = {'dir': '/profile',
                'submit': 'Upload',
                'action': 'Upload'
                }
        reply = tested_app.post('/profile', data=data)
        body = json.loads(str(reply.data, 'utf8'))
        self.assertEqual(reply.status_code, 400)
        self.assertEqual(body, {'msg': 'No selected file'})

        # change profile pic : invalid format
        filename = os.path.join(os.path.dirname('monolith/static/profile/'), 'test_invalid_format.txt')
        data = {'dir': '/profile',
                'submit': 'Upload',
                'action': 'Upload',
                'file': (open(filename, 'rb'), filename)
                }
        reply = tested_app.post('/profile', data=data)
        body = json.loads(str(reply.data, 'utf8'))
        self.assertEqual(reply.status_code, 400)
        self.assertEqual(body, {'msg': 'Invalid file format: <png>, <jpg> and <jpeg> allowed'})

        # change profile pic
        filename = os.path.join(os.path.dirname('monolith/static/profile/'), 'default.png')
        data = {'dir': '/profile',
                'submit': 'Upload',
                'action': 'Upload',
                'file': (open(filename, 'rb'), filename)
                }
        reply = tested_app.post('/profile', data=data)
        self.assertEqual(reply.status_code, 200)

        # report 1
        data = {'dir': '/users',
                'submit': 'Report', 
                'action': 'Report',
                'email': 'toreject@toreject'}
        reply = tested_app.post('/users', data=data)
        body = json.loads(str(reply.data, 'utf8'))
        self.assertEqual(reply.status_code, 200)
        self.assertEqual(body, {"msg":"User successfully reported"})
        
        # report 2
        data = {'dir': '/users',
                'submit': 'Report', 
                'action': 'Report',
                'email': 'toban1@toban1'}
        reply = tested_app.post('/users', data=data)
        body = json.loads(str(reply.data, 'utf8'))
        self.assertEqual(reply.status_code, 200)
        self.assertEqual(body, {"msg":"User successfully reported"})

        # block 
        data = {'dir': '/users',
                'submit': 'Block', 
                'action': 'Block',
                'email': 'toreject@toreject'}
        reply = tested_app.post('/users', data=data)
        self.assertEqual(reply.status_code, 200)

        # block 2
        data = {'dir': '/users',
                'submit': 'Block', 
                'action': 'Block',
                'email': 'toban1@toban1'}
        reply = tested_app.post('/users', data=data)
        self.assertEqual(reply.status_code, 200)

        # unblock on /users
        data = {'dir': '/users',
                'submit': 'Unblock', 
                'action': 'Unblock',
                'email': 'toreject@toreject'}
        reply = tested_app.post('/users', data=data)
        self.assertEqual(reply.status_code, 200)

        # /blacklist
        reply = tested_app.get('blacklist')
        self.assertEqual(reply.status_code, 200)

        # unblock on /blacklist
        data = {'dir': '/blacklist',
                'submit': 'Unblock', 
                'unblock': 'toban1@toban1'
                }
        reply = tested_app.post('/blacklist', data=data)
        self.assertEqual(reply.status_code, 200)


        print("COMMON USER: OK")


    # general tests for admin
    @pytest.mark.run(order=2)
    def test_admin(self):
        tested_app = app.test_client()

        # create dummy account 3
        reply = tested_app.post('/create_user',
                    data=json.dumps(self.create_toban2_user),
                    content_type='application/json', follow_redirects=True)
        self.assertEqual(reply.status_code, 200)

        # /profile without login
        reply = tested_app.get('/profile')
        self.assertEqual(reply.status_code, 401)

        # login
        reply = tested_app.post('/login', data=json.dumps(self.admin), content_type='application/json')
        self.assertEqual(reply.status_code, 302)

        # /profile
        reply = tested_app.get('/profile')
        self.assertEqual(reply.status_code, 200)

        # /users
        reply = tested_app.get('/users')
        self.assertEqual(reply.status_code, 200)


        # create todelete account
        reply = tested_app.post('/create_user',
                    data=json.dumps(self.create_todelete_user),
                    content_type='application/json', follow_redirects=True)
        self.assertEqual(reply.status_code, 200)
        # /delete_user
        reply = tested_app.get('/delete_user')
        self.assertEqual(reply.status_code, 200)

        # delete user
        data = {'dir': '/delete_user',
                'submit': 'Submit', 
                'firstname': 'todelete'}
        reply = tested_app.post('/delete_user', data=data)
        self.assertEqual(reply.status_code, 302)


        # /reported_users
        reply = tested_app.get('reported_users')
        self.assertEqual(reply.status_code, 200)

        # change profile pic : no selected file
        data = {'dir': '/profile',
                'submit': 'Upload',
                'action': 'Upload'}
        reply = tested_app.post('/profile', data=data)
        body = json.loads(str(reply.data, 'utf8'))
        self.assertEqual(reply.status_code, 400)
        self.assertEqual(body, {'msg': 'No selected file'})

        # change profile pic : invalid format
        filename = os.path.join(os.path.dirname('monolith/static/profile/'), 'test_invalid_format.txt')
        data = {'dir': '/profile',
                'submit': 'Upload',
                'action': 'Upload',
                'file': (open(filename, 'rb'), filename)
                }
        reply = tested_app.post('/profile', data=data)
        body = json.loads(str(reply.data, 'utf8'))
        self.assertEqual(reply.status_code, 400)
        self.assertEqual(body, {'msg': 'Invalid file format: <png>, <jpg> and <jpeg> allowed'})

        # change profile pic
        filename = os.path.join(os.path.dirname('monolith/static/profile/'), 'default.png')
        data = {'dir': '/profile',
                'submit': 'Upload',
                'action': 'Upload',
                'file': (open(filename, 'rb'), filename)
                }
        reply = tested_app.post('/profile', data=data)
        self.assertEqual(reply.status_code, 200)

        # block 
        data = {'dir': '/users',
                'submit': 'Block', 
                'action': 'Block',
                'email': 'toreject@toreject'}
        reply = tested_app.post('/users', data=data)
        self.assertEqual(reply.status_code, 200)

        # block 2
        data = {'dir': '/users',
                'submit': 'Block', 
                'action': 'Block',
                'email': 'toban1@toban1'}
        reply = tested_app.post('/users', data=data)
        self.assertEqual(reply.status_code, 200)

        # unblock on /users
        data = {'dir': '/users',
                'submit': 'Unblock', 
                'action': 'Unblock',
                'email': 'toreject@toreject'}
        reply = tested_app.post('/users', data=data)
        self.assertEqual(reply.status_code, 200)

        # /blacklist
        reply = tested_app.get('blacklist')
        self.assertEqual(reply.status_code, 200)

        # unblock on /blacklist
        data = {'dir': '/blacklist',
                'submit': 'Unblock', 
                'unblock': 'toban1@toban1'
                }
        reply = tested_app.post('/blacklist', data=data)
        self.assertEqual(reply.status_code, 200)

        # reject reported user
        data = {'dir': '/reported_users',
                'submit': 'Reject', 
                'action': "Reject",
                'email': 'toreject@toreject'
                }
        reply = tested_app.post('/reported_users', data=data)
        self.assertEqual(reply.status_code, 200)

        # ban on /users endpoint
        data = {'dir': '/users',
                'submit': 'Ban', 
                'action': 'Ban',
                'email': 'toban2@toban2'
                }
        reply = tested_app.post('/users', data=data)
        self.assertEqual(reply.status_code, 200)

        # ban on /reported_users endpoint
        data = {'dir': '/reported_users',
                'submit': 'Ban', 
                'action': "Ban",
                'email': 'toban1@toban1'
                }
        reply = tested_app.post('/reported_users', data=data)
        self.assertEqual(reply.status_code, 200)

        # logout
        reply = tested_app.get('/logout')
        self.assertEqual(reply.status_code, 302)

        # try login as banned 1
        reply = tested_app.post('/login', data=json.dumps(self.toban1_user), content_type='application/json')
        body = json.loads(str(reply.data, 'utf8'))
        self.assertEqual(reply.status_code, 403)
        self.assertEqual(body, {'msg': 'Your account has been permanently banned!'})

        # try login as banned 2
        reply = tested_app.post('/login', data=json.dumps(self.toban2_user), content_type='application/json')
        body = json.loads(str(reply.data, 'utf8'))
        self.assertEqual(reply.status_code, 403)
        self.assertEqual(body, {'msg': 'Your account has been permanently banned!'})

        print("ADMIN USER: OK")


    # /unregister tests
    @pytest.mark.run(order=3)
    def test_unregister(self):
        tested_app = app.test_client()

        # get /unregister without login
        reply = tested_app.get('/unregister')
        self.assertEqual(reply.status_code, 401)

        # create tounregister account
        reply = tested_app.post('/create_user',
                    data=json.dumps(self.create_tounregister_user),
                    content_type='application/json', follow_redirects=True)
        self.assertEqual(reply.status_code, 200)

        # login
        reply = tested_app.post('/login', data=json.dumps(self.tounregister_user), content_type='application/json')
        self.assertEqual(reply.status_code, 302)

        # get /unregister
        reply = tested_app.get('/unregister')
        self.assertEqual(reply.status_code, 200)

        # unregister with wrong password
        data = {'dir': '/unregister',
                'submit': 'Confirm', 
                'password': 'Incorrectpw1@'}
        reply = tested_app.post('/unregister', data=data)
        self.assertEqual(reply.status_code, 400)

        # unregister
        data = {'dir': '/unregister',
                'submit': 'Confirm', 
                'password': 'Tounregister1@'}
        reply = tested_app.post('/unregister', data=data)
        self.assertEqual(reply.status_code, 302)

        print("UNREGISTER USER: OK")
