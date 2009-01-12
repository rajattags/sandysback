from sandy2.di import Injector

import unittest

import time

def log(msg):
    print str(msg)

class InjectorTest(unittest.TestCase):

    
    def setUp(self):
        self.debug = False
        d = {'greeting' : 'Hallo', 'greetee' : 'World', 'integer' : 1}
        self.dict = d
        self.di = Injector(**d) 
        
    def testConfigure(self):
        obj = DummyObject()
        obj.greeting = None
        obj.greetee = None
        
        log("testConfigure: check simple case works")
        self.di.configure(obj)
        self.assertEquals(self.dict['greeting'], obj.greeting)
        self.assertEquals(self.dict['greetee'], obj.greetee)
        self.assertEquals(-1, obj.counter())
        self.printObj(obj)
        
        log("testConfigure: check private attributes can be addressed")
        # now test private variables (and more specific addressing)
        self.di['_DummyObject__counter'] = 42
        self.di.configure(obj)
        self.assertEquals(42, obj.counter())
        self.printObj(obj)
        
        log("testConfigure: no monkey patching")
        self.assertFalse(hasattr(obj, 'integer'))
        
        log("testConfigure: __setitem__ adds functions (i.e. no different from anything else)")
        self.di['function'] = lambda: 7
        obj.function = None
        
        self.di.configure(obj)
        self.assertEquals(7, obj.function())
    
    def testPerInstance(self):
        log("testPerInstance: Test that lambdas get called")
        obj = DummyObject()
        obj.greeting = None
        
        self.di.per_instance(greeting = lambda x: "WELCOME!")
        self.di.configure(obj)
        self.assertEquals("WELCOME!", obj.greeting)
        self.printObj(obj)
        
        
        log("testPerInstance: Test that the same lambda gets called each time")
        g = self.generator()
        self.di.per_instance(callCount = lambda x : g.next())
        
        for n in range(0, 100):
            # subsequent times we call should not give the same answer.
            t1 = self.di['callCount']
            self.assertEquals(n, t1)


    def testMultiArguments(self):
        self.di.per_instance(g0 = lambda: "0")
        self.assertEquals("0", self.di['g0'])

        self.di.per_instance(g1 = lambda x: "1")
        self.assertEquals("1", self.di['g1'])

        self.di.per_instance(g2 = lambda x, y='2': y)
        self.assertEquals("2", self.di['g2'])
        
        self.di.per_instance(g3 = lambda x='1', y='2': x)
        self.assertEquals(None, self.di['g3']) # because we try None as the default argument.
    
        
    def generator(self): 
        x = -1
        while (True):
            x = x + 1
            yield x

    def testLazySingleton(self):
        log("testLazySingleton: Test that the singleton is only generated once")    
        
        g = self.generator()
        
        self.di.lazy_singleton(callCount = lambda x : g.next())
        
        # the first time we call, we create the instance
        t0 = self.di['callCount']
        
        for n in range(1, 10):
            # subsequent times we call should give the same answer.
            self.assertEquals(t0, self.di['callCount'])
            # but the clock itself should keep ticking.
            self.assertNotEquals(self.di['callCount'], g.next())

    def printObj(self, object):
        if self.debug:
            print object.__dict__

class DummyObject(object):
    def __init__(self):
        self.__counter = -1
        pass

    def counter(self):
        return self.__counter

if __name__ == "__main__":
    unittest.main()