from sandy2.common.messages import Message
from sandy2.common.re_dispatch import REDispatcher
from sandy2.transports.mailer import MailListener, MailParser

SUBJECT="email_subject"
ADDRESS="email_from"
ALL_TEXT="email_body"

class AccountRegistrationListener:
    
    def __init__(self, username=None, host=None, password=None):
        
        self.registration_username=username
        self.registration_host=host
        self.registration_password=password
        
    
        self.dispatcher_map={}
    
        self.__mail_listener = None
        self.__mail_parser = None
    
    def run(self):
        self.__mail_listener = MailListener(mailhost=self.registration_host, username=self.registration_username, password=self.registration_password, listener=self.__dispatch)
        self.__mail_parser = MailParser(self.registration_username)
        self.__mail_listener.start()
        
    def close(self):
        if self.__mail_listener:
            self.__mail_listener.close()
            
    def __dispatch(self, txt):
        email = self.__mail_parser.parse_raw_mail(txt)
        message = Message(self.__mail_parser.find_metadata(email))
        
        for key, dispatcher in self.dispatcher_map.items():
            string = message.get(key, "")
            dispatcher.search(string, message)
    
    def add_rule(self, pattern, callable, match_on=ALL_TEXT):
        """Add a rule based upon the contents of a message emailed by a third-party indicating a signup/follow of us.
        This is done with a regular expression pattern and a function which is called if matched."""
        dispatcher = self.dispatcher_map.setdefault(match_on, REDispatcher(None))
        dispatcher.register_pattern(pattern, callable)