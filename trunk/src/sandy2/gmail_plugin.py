from sandy2.common.parsing import Parser, IMessageAction
from sandy2.common.plugins import IPlugin
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
        self.mail_receiver = None
        self.gmail_dao = None
        
    def install(self, ctx):
        gmail_user = self.properties['gmail_user'] 
        gmail_password = self.properties['gmail_password']

        if not self.mail_parser:
            self.mail_parser = MailParser(email_address=gmail_user, fullname=self.properties['agent_name'])
        if not self.mail_sender:
            self.mail_sender = MailSender(username=gmail_user, password=gmail_password)
        if not self.mail_receiver:
            self.mail_receiver = MailListener(username=gmail_user, password=gmail_password, listener=self.parse_mail)
        
        if not self.gmail_dao:
            self.gmail_dao = GmailDAO(self.database)
        
        ctx.er.transport_dao.add('email', self.gmail_dao)
        
        
    def start_up(self, ctx):
        ctx.er.parser_actions.add(EmailSender(sender=self.mail_sender, parser=self.mail_parser))
        ctx.er.template_files.add(self, 'ui/templates/email.txt')
        
    def run(self):
        self.mail_receiver.start()
        
    def parse_mail(self, txt):
        message = self.mail_parser.parse_raw_mail(txt)
        metadata = self.mail_parser.find_metadata(message)
        self.parser.process_dictionary(metadata)
    
    def stop(self):
        self.mail_receiver.close()
        self.mail_sender.disconnect()
                
class EmailSender(IMessageAction):
    def __init__(self, sender=None, parser=MailParser()):
        self.is_preceeded_by = ['output_message']
        self.mail_sender = sender
        self.mail_parser = parser
        
    def perform_action(self, metadata):
        if metadata.get('output_medium', None) == 'email':
            email = self.mail_parser.construct_email(metadata, key="output_message")
            self.mail_sender.send(email)

from sandy2.data.dao import SimpleDAO
from sandy2.data.linqish import SQLOperand, SQLCommand, SQLQuery
from sandy2.data.linqish_db import *

class GmailDAO(SimpleDAO):

    def __init__(self, database=None):
        self.database = database
    
    def create_tables(self):
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
            print "Table %s already exists. Not re-creating." % (email._name)
    
    def update_tables(self):
        pass
    
    def save_row(self, metadata):
        tx = metadata.tx

        row = tx.schema.email('e')
        row.user_id = metadata['user_id']
        row.email = metadata['email_id']
        row.is_verified = True

        query = s.insert_into(row)
        metadata.tx.execute(query)

    
    def find_row(self, params, results=None):
        if not results:
            results = dict()
            
        if params.has_key('user_id'):
            self.find_row_by_user_id(params['user_id'], results, params.tx)
        else:
            self.find_user_id(params['email_id'], results, params.tx)

        if not params.has_key('email_subject') and params.has_key('incoming_message'):
            message = params['incoming_message']
            
            if message.find("\n")>= 0:
                subject, body = message.split("\n", 1)
            else:
                subject = message
            results['email_subject'] = subject
            
        return results
    
    def find_user_id(self, email_address, results={}, tx=None):
        s = tx.schema
        e = s.email('e')
        rows = tx.execute(s.select(e.user_id, e.is_verified).from_(e).where(e.email == email_address))

        # not set if not found.                        
        for (user_id, verified) in rows:
            results['user_id'] = user_id

    def find_row_by_user_id(self, user_id, results={}, tx=None):
        # ie. we have a user id, but need an email address
        # so this is probably a reminder.
        s = tx.schema
        e = s.email('e')
        rows = tx.execute(s.select(e.email, e.is_verified).from_(e).where(e.user_id == user_id))
                                
        for (email_address, verified) in rows:
            results['email_id'] = email_address
        