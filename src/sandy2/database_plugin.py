from sandy2.common.sqlobject import *
from sandy2.common.plugins import IPlugin
from sandy2.common.parsing import IMicroParser

class DatabasePlugin(IPlugin):
    def __init__(self, properties={}, parser=None):
        self.is_followed_by = ['database']
        self.properties = properties
        self.parser = parser
        
    def install(self):
        path = self.properties.get('db.install.path', ':memory:')
        self.db = DB(path)
        
        # we should check if we already created this. 
        self.properties['database'] = self.db
        self.db.create_table('user', 'id integer primary key', 'fullname text', 'timezone_offset integer', 'reminder_medium text')
        self.db.create_table('message', 'id integer primary key', 'user integer', 'input_medium text', 'message')

        
    def start_up(self):
        self.parser.add_micro_parser(NewUserCreator())

class NewUserCreator(IMicroParser):
    def __init__(self, db=None, parser=None):
        self.is_preceeded_by = ['user', 'user_id', 'reply_message']
        self.is_followed_by = ['create_new_user']
        self.database = db
        self.parser=parser

    def micro_parse(self, metadata):
        if not metadata.get('reply_message', None): 
            return
        user_id = metadata.get('user_id', None)
        if user_id is None:
            # we don't need to respond to anything from a stranger that we don't understand.                            
                metadata['create_new_user'] = True
                table = self.database.table('user')
                id = table.id()
                table.insert(id, metadata['fullname'], metadata['tz_offset'], metadata['input_medium'])
                metadata['user_id'] = id
        else:
                metadata['create_new_user'] = False
                rows = self.database.from_('user').\
                                        select('fullname', 'reminder_medium', 'timezone_offset').\
                                        where('id = ?', user_id)

                for (name, medium, tz_offset) in rows:
                    metadata['fullname'] = name
                    metadata['reminder_medium'] = medium
                    metadata['tz_offset'] = tz_offset
                    return

    
                                                   