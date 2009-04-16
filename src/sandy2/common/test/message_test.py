import unittest

from sandy2.common.parsing import Message

class MessageTest(unittest.TestCase):
    
    def setUp(self):
        self.dict = dict()
        self.message = Message(self.dict)
        
    def testDictionary(self):
        obj = object()
        
        
        self.dict['obj'] = obj
        self.assertTrue(obj is self.message['obj'])
        
    def testAddDictionary(self):
        
        self.message['zero'] = 0
        self.assertEquals(0, self.message['zero'])
        
        m = dict()
        m['one'] = 1
        self.message.add_dictionary(m)
        
        self.assertEquals(0, self.message['zero'])
        self.assertEquals(1, self.message['one'])

        self.message.add_dictionary(lambda x: 2)
        self.assertEquals(0, self.message['zero'])
        self.assertEquals(1, self.message['one'])
        self.assertEquals(2, self.message['two'])
        self.assertEquals(2, self.message['three'])
        
    def testTemplate(self):
        self.message['zero'] = 0
        m = dict()
        m['one'] = 1
        self.message.add_dictionary(m)
        self.message.add_dictionary(lambda x: 2)

        self.assertEquals("0, 1, 2", "%(zero)s, %(one)s, %(two)s" % self.message)

if __name__ == "__main__":
    unittest.main()