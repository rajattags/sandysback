from sandy2.common.parsing import IMicroParser, IMessageAction, Parser
from sandy2.common.plugins import IPlugin
from sandy2.data.linqish import SQLOperand, SQLCommand, SQLQuery
from sandy2.data.linqish_db import *
from sandy2.transports.twitterer2 import TwitterService

from twitter import Twitter

class TwitterPlugin(IPlugin):
   def __init__(self, parser=None, db=None, properties={}):
      self.is_preceeded_by = ['database', 'passwords', 'servicecfg_database']
      self.is_followed_by = ['twitter_database']
      self.parser = parser
      self.database = db
      self.properties = properties

   def install(self, ctx):
      self.twitter_user = self.properties['twitter_user']
      self.twitter_pass = self.properties['twitter_password']

      self._twitter = self._new_twitter()
      self.__listener = TwitterService(self._new_twitter(), listener=self.receive_new_dm)

      

   def start_up(self, ctx):
      ctx.er.account_registrations.add("(?P<fullname>.*?) \((?P<twitter_name>\w+)\) is now following your updates on Twitter.", self.register_new_user)
      ctx.er.transport_dao.add('twitter', TwitterDAO(self.database))
      ctx.er.parser_actions.add(TwitterSender('twitter', self.__listener.send))
      ctx.er.template_files.add(self, 'ui/templates/twitter_templates.txt')

   def register_new_user(self, message):
      print "New follower: %s, will try and follow back" % (message['twitter_name'])
      self._twitter.friendships.create(screen_name=message['twitter_name'])

   def receive_new_dm(self, message):
      message['input_medium'] = 'twitter'
      self.parser.process_dictionary(message)

   def _new_twitter(self):
      return Twitter(self.twitter_user, self.twitter_pass)

   def run(self):
      self.__listener.start()
       
   def stop(self):
      self.__listener.close()

class TwitterSender(IMessageAction):
    def __init__(self, medium='twitter', sender=None):
        self.is_preceeded_by = ['output_message', 'output_medium']
        self._medium = medium
        self._sender = sender
    
    def perform_action(self, metadata):
        if metadata['output_medium'] == self._medium:
            self._sender(metadata)

class TwitterDAO:

    def __init__(self, database=None):
        self.database = database
    
    def create_tables(self):
        schema = self.database.schema
        tweets = schema.twitter('t')
        user = schema.user('u')
        
        table = schema.create_table(tweets)
        table.twitter_id(int).primary_key()
        table.twitter_name(str).primary_key()
        table.user_id(int).foreign_key(user.id)
        table.is_verified(bool)
        
        if (tweets._name not in self.database.get_tablenames()):
           tx = self.database.new_transaction()
           tx.execute(table)
           tx.commit()
           tx.close()
        else:
            print "Table %s already exists. Not re-creating." % (tweets._name)

    
    def update_tables(self):
        pass
    
    def save_row(self, metadata):
        tx = metadata.tx
        
        t = tx.schema.twitter('t')
        
        t.user_id = metadata['user_id']
        t.twitter_id = metadata['twitter_id']
        t.twitter_name = metadata['twitter_name']
        t.is_verified = True

        query = tx.schema.insert_into(t)
        tx.execute(query)

    
    def find_row(self, params, results=None):
        if not results:
            results = dict()
            
        if params.has_key('user_id'):
            self.find_row_by_user_id(params['user_id'], results, params.tx)
        else:
            self.find_user_id(params['twitter_id'], results, params.tx)
        return results
    
    def find_user_id(self, twitter_id, results={}, tx=None):
        s = tx.schema
        t = s.twitter('t')
        rows = tx.execute(s.select(t.user_id, t.is_verified).from_(t).where(t.twitter_id == twitter_id))

        # not set if not found.                        
        for (user_id, verified) in rows:
            results['user_id'] = user_id

    def find_row_by_user_id(self, user_id, results={}, tx=None):
        # ie. we have a user id, but need an email address
        # so this is probably a reminder.
        s = tx.schema
        e = s.twitter('t')
        rows = tx.execute(s.select(e.twitter_id, e.twitter_name, e.is_verified).from_(e).where(e.user_id == user_id))
                                
        for (twitter_id, twitter_name, verified) in rows:
            results['twitter_id'] = twitter_id
            results['twitter_name'] = twitter_name
        