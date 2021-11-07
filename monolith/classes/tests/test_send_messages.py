# import json
# import os,io
# from typing import Text
# import unittest
# import flask 
# from bs4 import BeautifulSoup as bs
# from werkzeug import test
# import monolith.background as bg

# from ...views.messages import filter_language
# from ...database import Message

# from monolith.app import app

# '''TEST ENDPOINT AND FUNCTION TO WRITE,SEND,SAVE MASSEGES'''
# class Test(unittest.TestCase):

#     def __init__(self, *args, **kw):
#         super(Test, self).__init__(*args, **kw)
#         '''USERS TEST VECTORS'''
#         self.sender = {
#             'email': 's@test.com',
#             'password': 'Sender1@',
#         }

#         self.recipient = {
#             'email': 'r@test.com',
#             'password': 'Sender1@'
#         }     
#         self.admin = {
#             'email': 'admin@test.com',
#             'password': 'Admin1@',
#         }
   

#     #Setup ENV
#     def setUp(self):
#         app.config['TESTING'] = True
#         app.config['WTF_CSRF_ENABLED'] = False
#         app.secret_key = 'ANOTHER ONE'



#     #TEST MESSAGE CREATION AND DELIVERY
#     def test_message_post(self): 
#         tested_app = app.test_client()
        
#         #Message test vector SAVE
#         self.message = {
#             'text_area': 'text',
#             'delivery_date': '2022-10-10T08:00',
#             'save_button':'Save'
#         }

#         # Check POST create_message SAVE
#         tested_app.post('/login', data=json.dumps(self.sender), content_type='application/json')
#         reply = tested_app.post('/create_message', data=json.dumps(self.message), content_type='application/json')
#         self.assertEqual(reply.status_code, 302)

#         #Message test vector SAVE+HIDDEN
#         self.message = {
#             'message_id_hidden':1,
#             'text_area': 'text',
#             'delivery_date': '2022-10-10T08:00',
#             'save_button':'Save'
#         }

#         # Check POST create_message SAVE+HIDDEN
#         tested_app.post('/login', data=json.dumps(self.sender), content_type='application/json')
#         reply = tested_app.post('/create_message', data=json.dumps(self.message), content_type='application/json')
#         self.assertEqual(reply.status_code, 302)

#         #Message test vector SEND
#         self.message = {
#             'text_area': 'text',
#             'delivery_date': '2022-10-10T08:00',
#             'users_list':'1',
#             'send_button':'Send'
#         }

#         # Check POST create_message SEND
#         tested_app.post('/login', data=json.dumps(self.sender), content_type='application/json')
#         reply = tested_app.post('/create_message', data=json.dumps(self.message), content_type='application/json')
#         self.assertEqual(reply.status_code, 302)

#         #Message test vector SEND+HIDDEN
#         self.message = {
#             'message_id_hidden':1,
#             'text_area': 'text',
#             'delivery_date': '2022-10-10T08:00',
#             'users_list':'1',
#             'send_button':'Send'
#         }

#         # Check POST create_message SEND+HIDDEN
#         tested_app.post('/login', data=json.dumps(self.sender), content_type='application/json')
#         reply = tested_app.post('/create_message', data=json.dumps(self.message), content_type='application/json')
#         self.assertEqual(reply.status_code, 302)

#         #ERRORS

#         #Message test vector SEND wrong date        
#         self.message = {
#             'text_area': 'text',
#             'delivery_date': '2021-10-10T08:00',
#             'users_list':'1',
#             'send_button':'Send'
#         }

#         # Check POST create_message SEND with wrong date
#         tested_app.post('/login', data=json.dumps(self.sender), content_type='application/json')
#         reply = tested_app.post('/create_message', data=json.dumps(self.message), content_type='application/json')
#         self.assertEqual(reply.status_code, 409)

#         #Message test vector SEND without recipient
#         self.message = {
#             'text_area': 'text',
#             'delivery_date': '2022-10-10T08:00',
#             'send_button':'Send'
#         }

#         # Check POST create_message SEND without recipient
#         tested_app.post('/login', data=json.dumps(self.sender), content_type='application/json')
#         reply = tested_app.post('/create_message', data=json.dumps(self.message), content_type='application/json')
#         self.assertEqual(reply.status_code, 409)
        
#         #Message test vector SAVE wrong date
#         self.message = {
#             'text_area': 'text',
#             'delivery_date': '2021-10-10T08:00',
#             'save_button':'Save'
#         }

#         # Check POST create_message SAVE with wrong date
#         tested_app.post('/login', data=json.dumps(self.sender), content_type='application/json')
#         reply = tested_app.post('/create_message', data=json.dumps(self.message), content_type='application/json')
#         self.assertEqual(reply.status_code, 409)


#     def test_message_read(self):
#         tested_app = app.test_client()

#         # Read message not logged in
#         reply = tested_app.get('/message/2')

#         # Read message logged in
#         tested_app.post('/login', data=json.dumps(self.sender), content_type='application/json')
#         reply = tested_app.get('/message/2')
#         self.assertEqual(reply.status_code, 200)

#         # Check bad language message
#         tocensor_message = Message()
#         Message.recipient_id = '1'
#         Message.delivery_date = '10/10/2022'
#         Message.text = 'Asshole'
#         self.assertEqual({'recipient_id': '1', 'delivery_date': '10/10/2022', 'text': '****'}, filter_language(tocensor_message))

#     #TEST THE SAVED MESSAGE RETRIEVE ENDPOINT
#     def test_message_get(self):
        
#         tested_app = app.test_client()

#         # Test with user not logged in.
#         # Create message
#         # Check GET create_message
#         reply = tested_app.get('/create_message')
#         self.assertEqual(reply.status_code, 401)

#         #Test Load Draft
#         reply = tested_app.get('/create_message?draft_id=2')
#         self.assertEqual(reply.status_code, 401)
#         #Test Forward
#         reply = tested_app.get('/create_message?forw_id=2')
#         self.assertEqual(reply.status_code, 401)
#         #Test Reply
#         reply = tested_app.get('/create_message?reply_id=2')
#         self.assertEqual(reply.status_code, 401)

#         # Login with the user
#         tested_app.post('/login', data=json.dumps(self.sender), content_type='application/json')

#         # Tests with user logged in.
#         # Create message
#         # Check GET create_message
#         reply = tested_app.get('/create_message')
#         self.assertEqual(reply.status_code, 200)

#         #Test Load Draft
#         reply = tested_app.get('/create_message?draft_id=2')
#         self.assertEqual(reply.status_code, 200)
        
      






        
        
        



