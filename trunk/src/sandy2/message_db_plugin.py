from sandy2.data.linqish_db import Transaction
from sandy2.data.linqish import Schema
from sandy2.common.plugins import IPlugin
from sandy2.common.parsing import IMicroParser

from sandy2.data.dao import SimpleDAO

text_length = 1024

class MessageDBPlugin(IPlugin):
    def __init__(self, properties={}, parser=None, db=None):
        self.is_preceeded_by = ['database']
        self.is_followed_by = ['scheduling']
        self.properties = properties
        self.parser = parser
        self.database = db
        self.message_dao = None

    def install(self, ctx):
        if self.message_dao is None:
            self.message_dao = MessageDAO(self.database)
            
        self.message_dao.create_tables()

    def start_up(self, ctx):
        ctx.er.parser_filters.add(MessageRecorder(self.message_dao))
        
        commands = MessageDBCommands(self.message_dao)
        ctx.er.message_patterns.add('^(lookup|look up|l) (?P<query_text>.*)', commands.lookup_command)
        
        ctx.er.template_files.add(self, 'ui/templates/message_commands.txt')

class MessageDBCommands:
    
    def __init__(self, message_dao):
        self.message_dao = message_dao
    
    def lookup_command(self, metadata):
        """lookup <something> :- find all the messages you've sent containing all the words in the query.
                e.g. look up Tom cell
                e.g. l book
        """
        metadata['command'] = 'lookup_command'
        results = self.message_dao.find_row(metadata)
        metadata.add_dictionary(results)
        
class MessageRecorder(IMicroParser):
    
    def __init__(self, dao):
        self.is_preceeded_by = ['user_id', 'input_medium', 'incoming_message', 'tx', 'command']
        self.is_followed_by = ['message_id']
        self.message_dao = dao
        
    def micro_parse(self, metadata):
        
        if not metadata.has_key('user_id') or metadata.get('is_reminder', False):
            return
        
        if metadata.get('command', None) not in ['lookup_command', None]:
            self.message_dao.save_row(metadata)
            
class MessageDAO(SimpleDAO):
    
    def __init__(self, db):
        SimpleDAO.__init__(self)
        self.database = db
        
    def create_tables(self):
        schema = self.database.schema
        message = schema.message('m')
        if (message._name not in self.database.get_tablenames()):
            
            table = schema.create_table(message)
            
            table.user_id(int)
            table.id(int).primary_key().auto_increment()
            table.text("text(%s)" % (text_length)).not_null()
            table.input_medium(str).not_null()
        
            tx = self.database.new_transaction()
            tx.execute(table)
            tx.commit()
            tx.close()
        else:
            print "Table %s already exists. Not re-creating." % (message._name)

    def update_table(self):
        pass
    
    def save_row(self, metadata):
        tx = metadata.tx
        schema = tx.schema
        m = schema.message('m')
        
        message_id = tx.next_id(m.id)
        m.id = message_id
        m.user_id = metadata['user_id']
        m.input_medium = metadata['input_medium']
        text = metadata['incoming_message']
        if len(text) >= text_length - 1:
            text = text[:text_length - 1]
        m.text = text 
        tx.execute(schema.insert_into(m))
        
        metadata['message_id'] = message_id  
    
    def find_row(self, params, results=None):
        results = SimpleDAO.find_row(self, params, results)
        
        tuples = []
        results['lookup_messages'] = tuples
        
        try:
            user_id = params['user_id']
            query_text = params['query_text']

            tokens = map(lambda s: s.lower().strip(), query_text.split())
            
            
            
            tx = params.tx
        
            schema = tx.schema
            
            
            
            m = schema.message('m')
            
            condition = None
            for t in tokens:
                clause = m.text.ilike("%%%s%%" % (t))
                if condition is None:
                    condition = clause
                else:
                    condition = condition & clause
                    
            condition = (m.user_id == user_id) & condition
            
            
            rows = tx.execute(schema.
                              select(m.id, m.text).
                              from_(m).
                              where(condition).
                              order_by(m.id) )
        
            for id, text in rows:
                tuples.append((text, id))
            
        except KeyError:
            pass
        
        return results