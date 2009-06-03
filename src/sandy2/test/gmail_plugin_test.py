import unittest
from sandy2.common.parsing import Parser
from sandy2.common.plugins import PluginFramework

from sandy2.common.di import Injector
from sandy2.transports.mailer import MailParser

from sandy2.base_plugin import BasicMicroParsingPlugin
from sandy2.database_plugin import DatabasePlugin
from sandy2.gmail_plugin import GmailPlugin
from sandy2.reminder_plugin import SchedulerPlugin
from sandy2.introspection_plugin import IntrospectionPlugin

import time
from datetime import datetime, timedelta

class EmailPluginTest(unittest.TestCase):
    
    def __init__(self, methodName):
        unittest.TestCase.__init__(self, methodName)
        
    
    def setUp(self):
        di = Injector()

        di['mail_sender'] = self.sender = DummyMailSender()
        self.mail_parser = MailParser(['zander.dev@gmail.com', 'zander.dev@googlemail.com'], "Zander The Wonderhorse")
        ps = PluginFramework(plugins=[DatabasePlugin(), GmailPlugin(), SchedulerPlugin(), BasicMicroParsingPlugin(), IntrospectionPlugin()], di = di)
        ps.configure()

        self.parser = ps.di['parser']
        self.assertNotEquals(None, self.parser)
        
    def testMessage(self):
        event = self.event()
        event = self.parser.parse(event)
        self.parser.perform_actions(event)
        
        tx = event.tx
        user = tx.schema.user('u')
        all_users = tx.execute(tx.schema.select(user).from_(user))
        self.assertTrue(len(all_users) > 0)
        
        
        
        
    def testMultiUser(self):
        event = self.event()
        self.parser.parse(event)
        self.parser.perform_actions(event)
        
        event = self.event()
        event['email_id'] = 'fred@freda.net'
        event['fullname'] = 'Fred Flintstone'
        event = self.parser.parse(event)
        self.parser.perform_actions(event)

        tx = event.tx
        user = tx.schema.user('u')
        all_users = tx.execute(tx.schema.select(user).from_(user))
        self.assertTrue(len(all_users) >= 2)
        
    def testTimedEvent(self):
        event = self.event()
        event['email_id'] = 'fred@freda.net'
        event['fullname'] = 'Fred Flintstone'
        event = self.parser.parse(event)
        self.parser.perform_actions(event)
        self.assertTrue(self.sender.last_message.startswith("Re:"))

        event = self.event()
        event['email_id'] = 'fred@freda.net'
        event['fullname'] = 'Fred Flintstone'
        event['message_datetime_local'] = datetime.utcnow()
        event['incoming_message'] = 'help in 3 seconds'
        
        event = self.parser.parse(event)
        self.parser.perform_actions(event)
        self.assertTrue(self.sender.last_message.startswith("Re:"))

        time.sleep(4)
        self.assertTrue(self.sender.last_message.startswith("REMINDER:"))
    
    def event(self):
        msg = self.mail_parser.parse_raw_mail(self.message())
    
        event = self.mail_parser.find_metadata(msg)
        return event
    
    def message(self):
        return """                                                                                                                                                                                                                                                               
Delivered-To: zander.dev@gmail.com
Received: by 10.140.208.13 with SMTP id f13cs1817rvg;
        Wed, 11 Feb 2009 13:11:53 -0800 (PST)
MIME-Version: 1.0
Received: by 10.181.234.13 with SMTP id l13mr22501bkr.123.1234386712255; Wed, 
    11 Feb 2009 13:11:52 -0800 (PST)
Date: Wed, 11 Feb 2009 21:11:52 +0000
Message-ID: <176b2d550902111311j48c97a02pa1ed7d921fe06465@mail.gmail.com>
Subject: Another tester
From: James Hugman <jameshugman@gmail.com>
To: zander.dev@gmail.com
Content-Type: text/plain; charset=ISO-8859-1
Content-Transfer-Encoding: 7bit

Remind me when it's time to stop.
"""

class DummyMailSender:
    
    def __init__(self):
        self.last_message = ''
        pass
    
    def connect(self):
        pass
    
    def send(self, mime):
        self.last_message = mime['Subject']
        print "Sending to %s: %s" % (mime['To'], self.last_message)
    
if __name__ == '__main__':
    unittest.main()