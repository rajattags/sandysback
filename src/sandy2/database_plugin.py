from sandy2.data.linqish import SQLOperand, SQLCommand, SQLQuery
from sandy2.data.linqish_db import *
from sandy2.common.plugins import IPlugin
from sandy2.common.parsing import IMicroParser

class DatabasePlugin(IPlugin):
    def __init__(self, properties={}, parser=None):
        self.is_followed_by = ['database']
        self.properties = properties
        self.parser = parser
        
    def install(self):
        self.db = DB(user="root", passwd="NOT_REALLY", db="zander_test_database", host="127.0.0.1", port=3306)
        # we should check if we already created this. 
        self.properties['database'] = self.db
        
        schema = self.db.schema
        schema.name = 'alpha_'

        user = schema.user('u')
        table = schema.create_table(user)
        
        table.fullname(str)
        table.id(int).primary_key()
        table.timezone_offset(int)
        table.reminder_medium(str)
            
        if (user._name not in self.db.get_tablenames()):
            tx = self.db.new_transaction()
            tx.execute(table)
            tx.commit()
            tx.close()
        else:
            print "Table %s already exists. Not re-creating." % (user._name)
        
#        self.db.create_table('user', 'id integer primary key', 'fullname varchar(100)', 'timezone_offset integer', 'reminder_medium varchar(10)')


        
    def start_up(self):
        self.parser.add_micro_parser(NewUserCreator())
        self.parser.add_micro_parser(NewTransactionAnnotater())
        

class NewUserCreator(IMicroParser):
    def __init__(self, db=None, parser=None):
        self.is_preceeded_by = ['user', 'user_id', 'reply_message', 'db']
        self.is_followed_by = ['create_new_user']
        self.database = db

    def micro_parse(self, metadata):
        if not metadata.get('reply_message', None): 
            # if we haven't got a valid message, then we haven't got a valid reply.
            # if that's the case, we shouldn't create a user.
            return
        user_id = metadata.get('user_id', None)
        if user_id is None:
            # we don't need to respond to anything from a stranger that we don't understand.                            
                metadata['create_new_user'] = True
                schema = metadata.tx.schema
                u = schema.user('u')

                

                tx = metadata.tx

                # definitely not v. thread safe.
                max_id = tx.execute(schema.select(u.id).max().from_(u))
                if len(max_id):
                    id = max_id[0][0]
                else:
                    id = 0 
            
                id = id + 1
                u.id = id
                u.fullname = metadata['fullname']
                u.timezone_offset = metadata['tz_offset']
                u.reminder_medium = metadata['input_medium']
                metadata['user_id'] = id
                tx.execute(schema.insert_into(u))
#                table.insert(id, metadata['fullname'], metadata['tz_offset'], metadata['input_medium'])
        else:
                metadata['create_new_user'] = False
                u = metadata.tx.schema.user('u')
                
                query = metadata.tx.schema.select(u.fullname, u.reminder_medium, u.timezone_offset).from_(u).where(u.id == user_id)
                
                rows = metadata.tx.execute(query)
                
#                rows = self.database.from_('user').\
#                                        select('fullname', 'reminder_medium', 'timezone_offset').\
#                                        where('id = ?', user_id)

                for (name, medium, tz_offset) in rows:
                    metadata['fullname'] = name
                    metadata['reminder_medium'] = medium
                    metadata['tz_offset'] = tz_offset
                    return
                
class NewTransactionAnnotater(IMicroParser):
    
    def __init__(self, db=None):
        self.is_followed_by = ['db']
        self.database = db
    
    def micro_parse(self, metadata):
        metadata.tx = self.database.new_transaction()