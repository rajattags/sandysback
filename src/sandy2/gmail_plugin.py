from sandy2.common.parsing import IMicroParser, IMessageAction, Parser
from sandy2.common.plugins import IPlugin
from sandy2.common.sqlobject import DB

class GmailPlugin(IPlugin):
    def __init__(self, parser=None, db=None, properties={}):
        self.is_preceeded_by = ['database']
        self.is_followed_by = ['email_database']
        self.parser = parser
        self.database = db
        self.properties = properties
        
    def install(self):
        self.database.create_table('email', 'email text primary key', 'user_id integer ', 'is_verified boolean')
    
    def start_up(self):
        self.parser.add_micro_parser(EmailUserFinder())
        self.parser.add_micro_parser(EmailUserCreator())
        
    
class EmailUserFinder(IMicroParser):

    def __init__(self, db=None):
        self.is_preceeded_by = ['input_medium', 'incoming_message']
        self.is_followed_by = ['user', 'user_id']
        self.database = db

    def micro_parse(self, metadata):
        if metadata['input_medium'] != 'email':
            return
        
        email_address = metadata['email_id']
        rows = self.database.from_('email').\
                                select('user_id', 'is_verified').\
                                where('email = ?', email_address)
                                
        for (user_id, verified) in rows:
            metadata['user_id'] = user_id


class EmailUserCreator(IMicroParser):
    def __init__(self, db=None, parser=None):
        self.is_preceeded_by = ['create_new_user']
        self.database = db
        self.parser = parser

    def micro_parse(self, metadata):
        if metadata.get('create_new_user', False):
            # we don't need to respond to anything from a stranger that we don't understand.
            if metadata['input_medium'] == 'email':
                user_id = metadata['user_id']
                self.database.into('email').insert(metadata['email_id'], user_id, True)
                # reparse, now we've inserted some stuff into the user table.
                self.parser.parse(metadata)