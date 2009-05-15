from sandy2.common.parsing import IMicroParser, IMessageAction, Parser
from sandy2.common.plugins import IPlugin
from sandy2.data.linqish import SQLOperand, SQLCommand, SQLQuery
from sandy2.data.linqish_db import *
from sandy2.transports.twitterer import TwitterListener

class IdenticaPlugin(IPlugin):
   def __init__(self, parser=None, db=None, properties={}):
      self.is_preceeded_by = ['database', 'passwords', 'servicecfg_database']
      self.is_followed_by = ['identica_database']
      self.parser = parser
      self.database = db
      self.properties = properties

   def install(self, ctx):
      self.identica_user = self.properties['identica_user']
      self.identica_pass = self.properties['identica_password']

      schema = self.database.schema
      identices = schema.identices('i')
      user = schema.user('u')

      table = schema.create_table(identices)
      table.notice_id(int).primary_key()
      table.identica_name(str)
      table.user_id(int).foreign_key(user.id)
      table.is_verified(bool)

      if (identices._name not in self.database.get_tablenames()):
         tx = self.database.new_transaction()
         tx.execute(table)
         tx.commit()
         tx.close()
      else:
         print "table %s already exists.  not re-creating." % (identices._name)

   def start_up(self, ctx):
      print "starting up...\n";

   def run(self):
      from threading import Thread

      class Listening(Thread):
         def __init__(self, outer):
            Thread.__init__(self)
            self.outer = outer
            self.receiver = TwitterListener(hostname='identi.ca/api', username=outer.identica_user, password=outer.identica_pass)

         def run(self):
            for msg in self.receiver.run():
               print "got %s man" % (msg.text)

      Listening(self).start()
