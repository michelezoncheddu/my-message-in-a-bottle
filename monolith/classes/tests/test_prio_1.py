import json
import unittest
import datetime

from monolith.app import app


class Test(unittest.TestCase):

    def __init__(self, *args, **kw):
        super(Test, self).__init__(*args, **kw)
        self.login_user = {
            'email': 'admin@admin',
            'password': 'admin'
        }

        self.login_user_fake = {
            'email': 'fake@fake.com',
            'password': 'fake'
        }

        self.create_user = {
            'email': 'test@tet.com',
            'firstname': 'testname',
            'lastname': 'testlastname',
            'password': 'testpassword',
            'dateofbirth': '9/10/2020',
            'location': 'Pisa'
        }



    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False

    def test_users(self):
        pass

    #sign_up
    def test_sign_up(self):
        tested_app = app.test_client()

        
        reply = tested_app.post('/create_user',
                    data=json.dumps(self.create_user),
                    content_type='application/json', follow_redirects=True)
        
        self.assertEqual(reply.status_code, 200)
    

    #login
    def test_login(self):
        tested_app = app.test_client()

        # login of unexistent user
        reply = tested_app.post('/login',
                    data=json.dumps(self.login_user_fake),
                    content_type='application/json', follow_redirects=True)
        
        self.assertEqual(reply.status_code, 200)
    

        # first time login user
        reply = tested_app.post('/login',
                    data=json.dumps(self.login_user),
                    content_type='application/json', follow_redirects=True)
        
        self.assertEqual(reply.status_code, 200)

        
    
    #logout
    def test_logout(self):
        pass


    # write a message
    def test_write_message(self):
        pass
