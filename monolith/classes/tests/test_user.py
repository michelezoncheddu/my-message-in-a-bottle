import os
import json
import unittest
import pytest


from monolith.app import app

from datetime import datetime, timedelta

from ...views.messages import filter_language
from ...database import Message
from ...utils import allowed_email, allowed_password, allowed_birth_date


class Test(unittest.TestCase):

    def __init__(self, *args, **kw):
        super(Test, self).__init__(*args, **kw)

        # Login admin user
        self.admin = {
            'email': 'admin@test.com',
            'password': 'Admin1@'
        }

        # Login user
        self.common_user = {
            'email': 's@test.com',
            'password': 'Sender1@'
        }

        # Creation of dummy user for unregister
        self.create_tounregister_user = {
            'email': 'tounregister@test.com',
            'firstname': 'tounregister',
            'lastname': 'tounregister',
            'password': 'Tounregister1@',
            'date_of_birth': '2020-10-09',
            'location': 'Pisa'
        }

        # Login of dummy user for unregister
        self.tounregister_user = {
            'email': 'tounregister@test.com',
            'password': 'Tounregister1@'
        }

        # Creation of dummy user for testing reject reported user
        self.create_toreject_user = {
            'email': 'toreject@test.com',
            'firstname': 'toreject',
            'lastname': 'toreject',
            'password': 'Toreject1@',
            'date_of_birth': '2020-10-09',
            'location': 'Pisa'
        }

        # Creation of dummy user for testing ban on endpoint users
        self.create_toban1_user = {
            'email': 'toban1@test.com',
            'firstname': 'toban1',
            'lastname': 'toban1',
            'password': 'Toban1@',
            'date_of_birth': '2020-10-09',
            'location': 'Pisa'
        }
        
        # Login
        self.toban1_user = {
            'email': 'toban1@test.com',
            'password': 'Toban1@'
        }

        # Creation of dummy user for testing ban on endpoint reported_users
        self.create_toban2_user = {
            'email': 'toban2@test.com',
            'firstname': 'toban2',
            'lastname': 'toban2',
            'password': 'Toban2@',
            'date_of_birth': '2020-10-09',
            'location': 'Pisa'
        }

        # Login
        self.toban2_user = {
            'email': 'toban2@test.com',
            'password': 'Toban2@'
        }


    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False


    # Test user actions
    @pytest.mark.run(order=1)
    def test_user(self):
        tested_app = app.test_client()

        # GET /create_user form
        reply = tested_app.get('/create_user')
        self.assertEqual(reply.status_code, 200)

        # Get profile of user not logged
        reply = tested_app.get('/profile')
        self.assertEqual(reply.status_code, 401)

        # Login user
        reply = tested_app.post('/login', data=json.dumps(self.common_user), content_type='application/json')
        self.assertEqual(reply.status_code, 302)

        # Get profile information of user
        reply = tested_app.get('/profile')
        self.assertEqual(reply.status_code, 200)

        # Save updates on profile
        data = {
                'action': 'Save'
        }

        reply = tested_app.post('/profile', data=data)
        self.assertEqual(reply.status_code, 200)

        # Get list of users
        reply = tested_app.get('/users')
        self.assertEqual(reply.status_code, 200)

        # Get list of reported_users without permission
        reply = tested_app.get('reported_users')
        self.assertEqual(reply.status_code, 401)

        # Change profile pic: no selected file
        data = {
                'action': 'Upload'
        }

        reply = tested_app.post('/profile', data=data)
        self.assertEqual(reply.status_code, 400)

        # Change profile pic: invalid format
        filename = os.path.join(os.path.dirname('monolith/static/profile/'), 'test_invalid_format.txt')
        data = {
                'action': 'Upload',
                'file': (open(filename, 'rb'), filename)
        }

        reply = tested_app.post('/profile', data=data)
        self.assertEqual(reply.status_code, 400)

        # Successfully change profile pic
        filename = os.path.join(os.path.dirname('monolith/static/profile/'), 'default.png')
        data = {
                'action': 'Upload',
                'file': (open(filename, 'rb'), filename)
        }
        reply = tested_app.post('/profile', data=data)
        self.assertEqual(reply.status_code, 200)

        # Toggle language filter: ON
        data = {
                'action': 'toggleFilter'
        }

        reply = tested_app.post('/profile', data=data)
        self.assertEqual(reply.status_code, 200)

        # Toggle language filter: OFF
        data = {
                'action': 'toggleFilter'
        }

        reply = tested_app.post('/profile', data=data)
        self.assertEqual(reply.status_code, 200)

        # Create user to report and not to be banned
        reply = tested_app.post('/create_user',
                    data=json.dumps(self.create_toreject_user),
                    content_type='application/json', follow_redirects=True)
        self.assertEqual(reply.status_code, 200)

        # Report 'toreject' user
        data = {
                'action': 'Report',
                'email': 'toreject@test.com'
        }
        reply = tested_app.post('/users', data=data)
        self.assertEqual(reply.status_code, 200)

        # Block  'toreject' user
        data = {
                'action': 'Block',
                'email': 'toreject@test.com'
        }
        reply = tested_app.post('/users', data=data)
        self.assertEqual(reply.status_code, 200)

        # Unblock 'toreject' users on endpoint users
        data = {
                'action': 'Unblock',
                'email': 'toreject@test.com'
        }

        reply = tested_app.post('/users', data=data)
        self.assertEqual(reply.status_code, 200)


        # Create user to report and to be banned
        reply = tested_app.post('/create_user',
                    data=json.dumps(self.create_toban1_user),
                    content_type='application/json', follow_redirects=True)
        self.assertEqual(reply.status_code, 200)

        
        # Report 'toban' user
        data = {
                'action': 'Report',
                'email': 'toban1@test.com'
        }
        reply = tested_app.post('/users', data=data)
        self.assertEqual(reply.status_code, 200)

        # Block 'toban' user
        data = {
                'action': 'Block',
                'email': 'toban1@test.com'
        }
        reply = tested_app.post('/users', data=data)
        self.assertEqual(reply.status_code, 200)

        
        # Get blacklist 
        reply = tested_app.get('blacklist')
        self.assertEqual(reply.status_code, 200)

        # Unblock 'toban' user on endpoint blacklist
        data = {
                'unblock': 'toban1@test.com'
        }
        reply = tested_app.post('/blacklist', data=data)
        self.assertEqual(reply.status_code, 200)


    # Tests admin actions
    @pytest.mark.run(order=2)
    def test_admin(self):
        tested_app = app.test_client()

        # create account to directly ban
        reply = tested_app.post('/create_user',
                    data=json.dumps(self.create_toban2_user),
                    content_type='application/json', follow_redirects=True)
        self.assertEqual(reply.status_code, 200)

        # Login admin
        reply = tested_app.post('/login', data=json.dumps(self.admin), content_type='application/json')
        self.assertEqual(reply.status_code, 302)

        # Get list of reported users
        reply = tested_app.get('reported_users')
        self.assertEqual(reply.status_code, 200)

        # Reject reported 'toreject' user
        data = {
                'action': "Reject",
                'email': 'toreject@test.com'
        }
        reply = tested_app.post('/reported_users', data=data)
        self.assertEqual(reply.status_code, 200)

        # Ban reported_users 'toban' on endpoint reported_users
        data = {'action': "Ban",
                'email': 'toban1@test.com'
        }
        reply = tested_app.post('/reported_users', data=data)
        self.assertEqual(reply.status_code, 200)

        # Directly ban 'toban2' on endpoint users
        data = {
                'action': 'Ban',
                'email': 'toban2@test.com'
        }
        reply = tested_app.post('/users', data=data)
        self.assertEqual(reply.status_code, 200)

        # Unban 'toban2' on endpoint users
        data = {
                'action': 'Unban',
                'email': 'toban2@test.com'
        }
        reply = tested_app.post('/users', data=data)
        self.assertEqual(reply.status_code, 200)


        # Logout admin
        reply = tested_app.get('/logout')
        self.assertEqual(reply.status_code, 302)

        # Failed login of banned user 'toban1'
        reply = tested_app.post('/login', data=json.dumps(self.toban1_user), 
                        content_type='application/json', follow_redirects=True)
        self.assertEqual(reply.status_code, 409)

        # Success login of unbanned user 'toban2'
        reply = tested_app.post('/login', data=json.dumps(self.toban2_user), 
                        content_type='application/json', follow_redirects=True)
        self.assertEqual(reply.status_code, 200)

    # Unregister and already registered tests
    @pytest.mark.run(order=3)
    def test_unregister(self):
        tested_app = app.test_client()


        # Unregister without login
        reply = tested_app.get('/unregister')
        self.assertEqual(reply.status_code, 401)

        # Create tounregister user
        reply = tested_app.post('/create_user',
                    data=json.dumps(self.create_tounregister_user),
                    content_type='application/json', follow_redirects=True)
        self.assertEqual(reply.status_code, 200)

        # Failed register of already registered email
        reply = tested_app.post('/create_user',
                    data=json.dumps(self.create_tounregister_user),
                    content_type='application/json', follow_redirects=True)
        self.assertEqual(reply.status_code, 409)

        # Login 'tounregister' user
        reply = tested_app.post('/login', data=json.dumps(self.tounregister_user), content_type='application/json')
        self.assertEqual(reply.status_code, 302)

        # Get unregister form
        reply = tested_app.get('/unregister')
        self.assertEqual(reply.status_code, 200)

        # Unregister with wrong password
        data = {
                'password': 'Incorrectpw1@'
        }
        reply = tested_app.post('/unregister', data=data)
        self.assertEqual(reply.status_code, 400)

        # Success unregister
        data = {
                'password': 'Tounregister1@'
        }
        reply = tested_app.post('/unregister', data=data)
        self.assertEqual(reply.status_code, 302)


    # Test for input fields format in create_user and bad language filter
    @pytest.mark.run(order=4)
    def test_info_validator(self):

        
        # Check bad language message
        tocensor_message = Message()
        Message.text = 'Asshole'
        now = datetime.now()
        Message.delivery_date = now
        Message.recipient_id = '1'
        Message.sender = '2'
        Message.recipient = '1'
        Message.is_draft = False
        Message.is_delivered = False
        self.assertEqual(
                {
                'text': '****',
                'delivery_date': now,
                'recipient_id': '1',
                'sender':'2',
                'recipient': '1',
                'is_draft': False,
                'is_delivered': False
                },
                filter_language(tocensor_message))
        

        # Invalid email
        invalid_email = "invalidemail"
        self.assertEqual(False, allowed_email(invalid_email))
        
        # Valid email
        valid_email = "valid@hotmail.com"
        self.assertEqual(True, allowed_email(valid_email))

        # Invalid password
        invalid_pw1 = "aaaa"                            # too short
        invalid_pw2 = "aaaaaaaaaaaaaaaaaaaaaaaaaa"      # too long
        invalid_pw3 = "password"                        # no upper case
        invalid_pw4 = "Password"                        # no numbers
        invalid_pw5 = "Password1"                       # no special characters
        self.assertEqual(False, allowed_password(invalid_pw1))
        self.assertEqual(False, allowed_password(invalid_pw2))
        self.assertEqual(False, allowed_password(invalid_pw3))
        self.assertEqual(False, allowed_password(invalid_pw4))
        self.assertEqual(False, allowed_password(invalid_pw5))
        
        # Valid password
        valid_pw = "Password1@"
        self.assertEqual(True, allowed_password(valid_pw))

        # Invalid birth date
        birth_invalid = datetime.today().date() + timedelta(days = 1)
        self.assertEqual(False, allowed_birth_date(birth_invalid))

        # Valid birth date
        birth_valid = datetime.today().date() - timedelta(days = 1)
        self.assertEqual(True, allowed_birth_date(birth_valid))


