import unittest
from sandy2.common.parsing import Parser
from sandy2.common.plugins import PluginSystem

from sandy2.transports.mailer import MailParser

from sandy2.gmail_plugin import *
from sandy2.database_plugin import DatabasePlugin
from sandy2.gmail_plugin import GmailPlugin

class EmailPluginTest(unittest.TestCase):
    def setUp(self):
        self.mail_parser = MailParser(['zander.alpha@gmail.com', 'zander.alpha@googlemail.com'], "Zander The Wonderhorse")
        ps = PluginSystem([DatabasePlugin(), GmailPlugin()])
        ps.configure()

        self.parser = ps.di['parser']
        self.assertNotEquals(None, self.parser)
        
    def testMessage(self):
        msg = self.mail_parser.parse_raw_mail(self.message())
    
        event = self.mail_parser.find_metadata(msg)
        event['reply_message'] = "Something random"
        self.parser.parse(event)
        
    
    def message(self):
        return """                                                                                                                                                                                                                                                               
Delivered-To: zander.alpha@gmail.com
Received: by 10.140.208.13 with SMTP id f13cs1817rvg;
        Wed, 11 Feb 2009 13:11:53 -0800 (PST)
MIME-Version: 1.0
Received: by 10.181.234.13 with SMTP id l13mr22501bkr.123.1234386712255; Wed, 
    11 Feb 2009 13:11:52 -0800 (PST)
Date: Wed, 11 Feb 2009 21:11:52 +0000
Message-ID: <176b2d550902111311j48c97a02pa1ed7d921fe06465@mail.gmail.com>
Subject: Another tester
From: James Hugman <jameshugman@gmail.com>
To: zander.alpha@gmail.com
Content-Type: text/plain; charset=ISO-8859-1
Content-Transfer-Encoding: 7bit

Remind me when it's time to stop.
"""
    
if __name__ == '__main__':
    unittest.main()