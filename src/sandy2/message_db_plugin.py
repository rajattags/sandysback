from sandy2.data.linqish_db import Transaction
from sandy2.data.linqish import Schema
from sandy2.common.plugins import IPlugin
from sandy2.common.parsing import IMicroParser

text_length = 1024

class MessageDBPlugin(IPlugin):
    def __init__(self, properties={}, parser=None, db=None):
        self.is_preceeded_by = ['database']
        self.is_followed_by = ['scheduling']
        self.properties = properties
        self.parser = parser
        self.database = db

    def install(self, ctx):
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


    def start_up(self, ctx):
        ctx.er.parser_filters.add(MessageRecorder())
        


class MessageRecorder(IMicroParser):
    
    def __init__(self):
        self.is_preceeded_by = ['user_id', 'input_medium', 'incoming_message', 'tx', 'command']
        self.is_followed_by = ['message_id']
        
    def micro_parse(self, metadata):
        
        if metadata.has_key('user_id') and metadata.has_key('command') and not metadata.get('is_reminder', False):
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