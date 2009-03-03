import unittest

import sandy2.common.scheduling

from threading import Timer
import time
from datetime import datetime, timedelta
    
class SchedulingTest(unittest.TestCase):
    
    def setUp(self):
        self.job_store = sandy2.common.scheduling.InMemoryJobStore()
        self.waiter = WaitForIt()
        self.sched = sandy2.common.scheduling.Scheduler(self.waiter.end, self.job_store)
        
    def testInterval(self):
        self.schedule(1, "1 seconds (and end)")
        self.waiting(1)
        
    def testOutOfOrder(self):
        self.schedule(5, "5 seconds (and end)")
        self.schedule(2, "2 seconds")
        self.schedule(1, "1 seconds")
        self.waiting(3)

    def testRestarting(self):
        self.schedule(1, "1 second (and end)")
        self.waiting(1)
        
        self.schedule(1, "1 second again, and end")
        self.waiting(1)
 
    def testPastEvents(self):
        # should have immediate execution.
        self.schedule(-1, "-1 second")
        self.schedule(0, "0 seconds")
        self.schedule(0.1, "0.1 seconds and end")
        self.waiting(3)
        
    def testConcurrentEvents(self):
        self.schedule(0.5, "first job")
        self.schedule(0.5, "second job")
        self.schedule(0.5, "third job")
        self.schedule(0.7, "end job")
        self.waiting(4)
        
    def testRestarting(self):
        self.schedule(0.5, "first")
        self.schedule(2.2, "second")
        self.schedule(2.5, "third")
        time.sleep(1)
        self.schedule(1.6, "fourth and end", 2.6)
        self.assertEquals(1, self.waiter.execution_count)
        
        self.sched.dispose()
        self.assertTrue(self.sched.is_disposed)
        
        # wait a second before creating another scheduler.
        time.sleep(1)
        
        self.sched = sandy2.common.scheduling.Scheduler(self.waiter.end, self.job_store)
        time.sleep(1)
        self.assertEquals(4, self.waiter.execution_count)
        
    def waiting(self, count):
        self.waiter.wait()
        self.assertEquals(count, self.waiter.execution_count)
        
    def schedule(self, seconds, id, expected=None):
        if not expected:
            expected = seconds
        dt = datetime.now() + timedelta(seconds=seconds)
#        dt = seconds
        self.sched.schedule(dt, id, expected)
    
class WaitForIt:
    def __init__(self):
        self.execution_count = 0
        self.running = True
        self.epsilon = 0.02
        self.datum = datetime.now()
        
    
    def end(self, id, seconds):
        self.execution_count += 1
        checkpoint = datetime.now() - self.datum
        seconds_test = sandy2.common.scheduling._td_to_s(checkpoint)
        print seconds_test, ": id =", id, "; wait =", seconds
        if seconds > 0:
            if seconds_test < seconds - self.epsilon or seconds_test > seconds + self.epsilon:
                raise AssertionError("Expected %s, was %s" % (seconds, seconds_test))
        self.running = (id.find("end") < 0)
    
    def wait(self):
        self.running = True
        self.datum = datetime.now()
        while self.running:
            time.sleep(1)
        
        
if __name__ == "__main__":
    unittest.main()