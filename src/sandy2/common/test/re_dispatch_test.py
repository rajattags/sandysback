import unittest

from sandy2.common.re_dispatch import *

class REDispatcherTest(unittest.TestCase):
    
    def setUp(self):
        pass
    
    def testRegistration(self):
        dispatcher = REDispatcher()
        
        r = dispatcher.register_pattern("test this", lambda x: 1)
        self.assertTrue(r.match("test this"))
        self.assertTrue(r.match("test   this"))

    def testDispatch(self):
        
        dis = REDispatcher()
        d = {}
        l = lambda match : d.__setitem__(match.group('mine'), 1)
        
        dis.register_pattern("(?P<mine>\d+)", l)
        
        dis.register_pattern("(?P<mine>telephone|tn)", l)
        
        dis.search("telephone 1234567")
        
        self.assertTrue(d.has_key('telephone'))
        self.assertTrue(d.has_key('1234567'))
        
        d.clear()
        dis.search("tn. 123")
        self.assertTrue(d.has_key('tn'))
        self.assertTrue(d.has_key('123'))
    
if __name__ == '__main__':
    unittest.main()