from sandy2.common.parsing import IMicroParser, IMessageAction, Parser
from sandy2.common.plugins import IPlugin
from sandy2.data.linqish import SQLOperand, SQLCommand, SQLQuery
from sandy2.data.linqish_db import *
from sandy2.transports.twitterer import TwitterListener

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
         print "table %s already exists.  not re-creating." % (tweets._name)

   def start_up(self, ctx):
      ctx.er.account_registration.add("(?P<fullname>.*?) \((?P<twitter_id>\w+)\) is now following your updates on Twitter.", self.register_new_user)


   def register_new_user(self, message):
      print "%s is one of us now. They go by the name of %s" % (message['twitter_id'], message['fullname'])

   def run(self):
       
      from threading import Thread

      class Listening(Thread):
         def __init__(self, outer):
            Thread.__init__(self)
            self.outer = outer
            self.receiver = TwitterListener(username=outer.twitter_user, password=outer.twitter_pass)

         def run(self):
            for msg in self.receiver.run():
               print "got %s man" % (msg.text)

#      Listening(self).start()
