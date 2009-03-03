import unittest

import parsedatetime.parsedatetime as pdt 
import parsedatetime.parsedatetime_consts as pdc 

from datetime import datetime, timedelta

class DateParserTest(unittest.TestCase):

    def _testTexts(self, texts):
        c = pdc.Constants()
        p = pdt.Calendar(c)
        for name, list in texts.items():
            print name
            for msg in list:
                dt = None
                (start, end, valid) = p.evalRanges(msg)
                if valid:
                    prefix = "Range:"
                    dt = (str(tuple_to_dt(start)), str(tuple_to_dt(end)))
                else:
                    (t, valid) = p.parse(msg)
                    if valid:
                        dt = str(tuple_to_dt(t))
                        if valid == 1:
                            prefix = "date :" 
                        elif valid == 2:
                            prefix = "time :" 
                        elif valid == 3:
                            prefix = "dt   :"                     
                    else:
                        dt = "INVALID"
                        prefix = "INVALID"
                    
                    
                print "\t", msg
                print "\t\t", prefix, dt
                print "\t\tEvent:", self.startTime(msg)

    def startTime(self, msg, constants=pdc.Constants()):
        parser = pdt.Calendar(constants)
        (start, end, valid) = parser.evalRanges(msg)
        
        if valid:
            return _dt(start)
        
        (start, valid) = parser.parse(msg)
        if valid == 1:
            # date
            return _dt(start)
        elif valid == 2:
            # time
            return _dt(start)
        elif valid == 3:
            # datetime
            return _dt(start)
        
        return None

        
    
    # see http://code.google.com/p/parsedatetime/wiki/Examples
    # and http://code.google.com/p/sandysBack
    def setUp(self):
        self.texts = self.verbose()
    
    def verbose(self):
        return {
            "calendar_examples" : [
                "Remind me about Literature 101 study group Mon 6-9pm @weekly",
                "Remind me to call Mom on her birthday on 9/16/07 @yearly @birthday",
                "Remember I work at the book store Tue 9-11:30am @work",
                "Remember I work at the book store Tues 9am-11:30am @work",
                "Remind me to wake up for my geometry midterm tomorrow at 7am.",
                "Remind me to ACTUALLY wake up for my midterm tomorrow at 7:30am."
            ], 
        
            "reminder_examples" : [
                "Remind me to move the car in 15 minutes",
                "Remind me to pick up the dry cleaning in 3 days",
                "Remind me to finish that TPS report by Monday morning"
            ], 
        
            "appointment_examples" : [
                "Remind me I have a Marketing meeting on 3/14 at 1-2pm",
                "Remember Sam's Tai Kwon Do belt test 6/1 10am-2pm",
                "Remind me about my haircut appointment on July 6 1-2pm",
                "Remind me to take out the trash on Sunday evening @weekly",
                "Remember to turn over the mattress tomorrow morning @monthly",
                "Remember to prepay taxes on Monday @quarterly",
                "Remember Mimi's birthday 7/8 @yearly"
            ],
        }
        
    def terse(self):
        return {
            "calendar_examples" : [
                "Mon 6-9pm",
                "9/16/07",
                "Tue 9-11:30am",
                "Tues 9am-11:30am",
                "tomorrow at 7am.",
                "tomorrow at 7:30am."
            ], 
        
            "reminder_examples" : [
                "in 15 minutes",
                "in 3 days",
                "Monday morning",
                "in 1 m"
            ], 
        
            "appointment_examples" : [
                "on 3/14 at 1-2pm",
                "6/1 10am-2pm",
                "July 6 1-2pm",
                "Sunday evening @weekly",
                "tomorrow morning @monthly",
                "on Monday @quarterly",
                "7/8"
            ],
        }    
    def testVerbose(self):
        self._testTexts(self.verbose())

    def testTerse(self):
        self._testTexts(self.terse())
                
def _dt(start):
    return datetime(*start[0:5])

def tuple_to_dt(t):
    return datetime(*t[0:5])

if __name__ == "__main__":
    unittest.main()
        