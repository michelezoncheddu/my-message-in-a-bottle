import unittest
import monolith.background as bg


'''TEST TO CHECK FUNCTIONS USED BY CELERY WORKERS TO EXECUTE SCHEDULED AND BROKERED TASKS'''
class Test(unittest.TestCase):
    def __init__(self, *args, **kw):
        super(Test, self).__init__(*args, **kw)


    '''TEST MESSAGE DELIVERY TASK.'''
    def test_send_messages(self):
        reply=bg.send_messages()
        self.assertEqual(reply, 'Delivered')


    '''TEST NOTIFY TASK.'''
    def test_notify(self):
        bg.notify(1,'test')


    '''TEST LOTTERY TASK'''
    def test_lottery(self):
        bg.lottery()
