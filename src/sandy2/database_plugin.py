from sandy2.data.linqish import SQLOperand, SQLCommand, SQLQuery
from sandy2.data.linqish_db import *
from sandy2.common.plugins import IPlugin
from sandy2.common.parsing import IMicroParser

class DatabasePlugin(IPlugin):
    def __init__(self, properties={}, parser=None):
        self.is_preceeded_by = ['passwords']
        self.is_followed_by = ['database']
        self.properties = properties
        self.parser = parser
        
    def install(self, ctx):
        di = self.properties
        
        
        self.db = DB(user=di['mysql_user'], passwd=di['mysql_password'], db=di['mysql_db'], host=di['mysql_host'], port=di['mysql_port'])
        # we should check if we already created this. 
        self.properties['database'] = self.db
        
        schema = self.db.schema
        schema.name = di.get('schema_prefix', '')

        user = schema.user('u')
        table = schema.create_table(user)
        
        table.fullname(str)
        table.id(int).primary_key()
        table.timezone_offset(int)
        table.reminder_medium(str)
        
        tx = None
        if (user._name not in self.db.get_tablenames()):
            tx = self.db.new_transaction()
            tx.execute(table)
            tx.commit()
            tx.close()
        else:
            print "Table %s already exists. Not re-creating." % (user._name)


        
    def start_up(self, ctx):
        ctx.er.parser_filters.add(NewUserCreator())
        ctx.er.parser_filters.add(UserPopulator())
        ctx.er.parser_filters.add(NewTransactionAnnotater())

class UserPopulator(IMicroParser):        
    def __init__(self):
        self.is_preceeded_by = ['user_id', 'tx']
        self.is_followed_by = ['fullname', 'tz_offset', 'reminder_medium']

    def micro_parse(self, metadata):
        user_id = metadata.get('user_id', None)
        if user_id is not None:
            metadata['create_new_user'] = False
            u = metadata.tx.schema.user('u')
            
            tx = metadata.tx
            query = tx.schema.select(u.fullname, u.reminder_medium, u.timezone_offset).from_(u).where(u.id == user_id)
            
            rows = tx.execute(query)
            

            for (name, medium, tz_offset) in rows:
                metadata['fullname'] = name
                metadata['reminder_medium'] = medium
                if not metadata.has_key('tz_offset'):
                    metadata['tz_offset'] = tz_offset
                else:
                    if metadata['tz_offset'] != tz_offset:
                        query = tx.schema.update(u).where_(u.id == user_id)
                        u.timezone_offset = metadata['tz_offset']
                        tx.execute(query)
                        tx.commit()

    def cleanup(self, metadata):
        if not metadata.has_key('user_id'):
            metadata['STOP'] = True


class NewUserCreator(IMicroParser):
    def __init__(self, db=None, parser=None):
        self.is_preceeded_by = ['user_id',  'tx', 'fullname', 'tz_offset', 'input_medium']
        self.is_followed_by = ['create_new_user', ]
        self.database = db

    def micro_parse(self, metadata):
        if not metadata.get('command', None): 
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
                
class NewTransactionAnnotater(IMicroParser):
    
    def __init__(self, db=None):
        self.is_followed_by = ['tx']
        self.database = db
    
    def micro_parse(self, metadata):
        metadata.tx = self.database.new_transaction()
        
    def cleanup(self, metadata):
        metadata.tx.commit()
        metadata.tx.close()