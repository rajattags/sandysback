from sandy2.common.parsing import IMicroParser, IMessageAction, Parser
from sandy2.common.plugins import IPlugin
from sandy2.data.linqish import SQLOperand, SQLCommand, SQLQuery
from sandy2.data.linqish_db import *
from sandy2.transports.mailer import MailListener, MailParser, MailSender




class GmailPlugin(IPlugin):
    def __init__(self, parser=None, db=None, properties={}):
        self.is_preceeded_by = ['database', 'passwords']
        self.is_followed_by = ['email_database']
        self.parser = parser
        self.database = db
        self.properties = properties
        self.mail_parser = None
        self.mail_sender = None
        
    def install(self, ctx):
        self.gmail_user = self.properties['gmail_user'] 
        self.gmail_password = self.properties['gmail_password']

        if not self.mail_parser:
            self.mail_parser = MailParser(email_address=self.gmail_user, fullname=self.properties['agent_name'])
        if not self.mail_sender:
            self.mail_sender = MailSender(username=self.gmail_user, password=self.gmail_password)
        
        schema = self.database.schema
        
        email = schema.email('e')
        user = schema.user('u')
        table = schema.create_table(email)
        
        table.email(str).primary_key()
        table.user_id(int).foreign_key(user.id)
        table.is_verified(bool)
            
        if (email._name not in self.database.get_tablenames()):
            tx = self.database.new_transaction()
            tx.execute(table)
            tx.commit()
            tx.close()
        else:
            print "Table %s already exists. Not re-creating." % (user._name)
    
    def start_up(self, ctx):
        ctx.er.micro_parsers.add(EmailUserFinder())
        ctx.er.micro_parsers.add(EmailUserCreator())
        ctx.er.parser_actions.add(EmailSender(sender=self.mail_sender, parser=self.mail_parser))
        
        ctx.er.template_files.add(self, 'ui/templates/email.txt')
        
    def run(self):
        
        from threading import Thread
        
        class Listening(Thread):
            def __init__(self, outer):
                Thread.__init__(self)
                self.outer = outer
                self.receiver = MailListener(username=outer.gmail_user, password=outer.gmail_password)
            
            def run(self):
                for txt in self.receiver.run():
                    message = self.outer.mail_parser.parse_raw_mail(txt)
                    metadata = self.outer.mail_parser.find_metadata(message)
                    self.outer.parser.parse(metadata)
                    self.outer.parser.perform_actions(metadata)
                    
            def close(self):
                self.receiver.close()
                
        self.mail_listener_thread = Listening(self)
        self.mail_listener_thread.start()
        
    
    def stop(self):
        self.mail_listener_thread.close()
        
class EmailUserFinder(IMicroParser):

    def __init__(self, db=None):
        self.is_preceeded_by = ['tx', 'input_medium', 'incoming_message']
        self.is_followed_by = ['user_id']
        self.database = db

    def micro_parse(self, metadata):
        if (metadata['input_medium'] != 'email'):
            return
        
        if metadata.has_key('user_id'):
            # ie. we have a user id, but need an email address
            # so this is probably a reminder.
            user_id = metadata['user_id']
            s = metadata.tx.schema
            e = s.email('e')
            rows = metadata.tx.execute(s.select(e.email, e.is_verified).from_(e).where(e.user_id == user_id))
                                    
            for (email_address, verified) in rows:
                metadata['email_id'] = email_address
            
            message = metadata['incoming_message']
            
            if message.find("\n")>= 0:
                subject, body = message.split("\n", 1)
            else:
                subject = message
            metadata['email_subject'] = subject
        else:
            
            email_address = metadata['email_id']

            s = metadata.tx.schema
            e = s.email('e')
            rows = metadata.tx.execute(s.select(e.user_id, e.is_verified).from_(e).where(e.email == email_address))

            # not set if not found.                        
            for (user_id, verified) in rows:
                metadata['user_id'] = user_id


class EmailUserCreator(IMicroParser):
    def __init__(self, db=None, parser=None):
        self.is_preceeded_by = ['tx', 'create_new_user']
        self.database = db
        self.parser = parser

    def micro_parse(self, metadata):
        if metadata.get('create_new_user', False):
            # we don't need to respond to anything from a stranger that we don't understand.
            if metadata['input_medium'] == 'email':
                s = metadata.tx.schema
                e = s.email('e')
                q = s.insert_into(e)
                e.user_id = metadata['user_id']
                e.email = metadata['email_id']
                e.is_verified = True
                metadata.tx.execute(q)



                # reparse, now we've inserted some stuff into the user table.
                self.parser.parse(metadata)
                
                
class EmailSender(IMessageAction):
    def __init__(self, sender=None, parser=MailParser()):
        self.is_preceeded_by = ['output_message']
        self.mail_sender = sender
        self.mail_parser = parser
        
    def perform_action(self, metadata):
        if metadata.get('output_medium', None) == 'email':
            email = self.mail_parser.construct_email(metadata, key="output_message")
            self.mail_sender.send(email)
