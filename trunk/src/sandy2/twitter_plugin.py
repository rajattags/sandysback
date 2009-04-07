from sandy2.common.parsing import IMicroParser, IMessageAction, Parser
from sandy2.common.plugins import IPlugin
from sandy2.data.linqish import SQLOperand, SQLCommand, SQLQuery
from sandy2.data.linqish_db import *
from sandy2.transports.twitterer import TwitterListener

tw_user = 'real_twitter_username';
tw_pass = 'real_twitter_password';

class TwitterPlugin(IPlugin):
   def __init__(self, parser=None, db=None, properties={}):
      self.is_preceeded_by = ['database']
      self.is_followed_by = ['twitter_database']
      self.parser = parser
      self.database = db
      self.properties = properties

   def install(self):
      schema = self.database.schema
      tweets = schema.twitter('t')
      user = schema.user('u')

      table = schema.create_table(tweets)
      table.twitter_id(int).primary_key()
      table.twitter_name(str)
      table.user_id(int).foreign_key(user.id)
      table.is_verified(bool)

      if (tweets._name not in self.database.get_tablenames()):
         tx = self.database.new_transaction()
         tx.execute(table)
         tx.commit()
         tx.close()
      else:
         print "table %s already exists.  not re-creating." % (user._name)

   def start_up(self):
      print "starting up...\n";

   def run(self):
      from threading import Thread

      class Listening(Thread):
         def __init__(self, outer):
            Thread.__init__(self)
            self.outer = outer

         def run(self):
            receiver = TwitterListener(username=tw_user, password=tw_pass)
            for msg in receiver.run():
               print "got %s man" % (msg.text)

      Listening(self).start()
