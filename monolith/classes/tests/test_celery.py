import unittest
import monolith.background as bg



class Test(unittest.TestCase):

    def __init__(self, *args, **kw):
        super(Test, self).__init__(*args, **kw)

    def test_do_task(self):
        reply=bg.do_task()
        self.assertEqual(reply, 'delivered')

    def test_notify(self):
        reply=bg.notify(1,'test') 
        self.assertEqual(reply, 'done')

    def test_lottery(self):
        bg.do_lottery()   
        #self.assertEqual(reply, 'Estratto')    

