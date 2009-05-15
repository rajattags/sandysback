from sandy2.common.plugins import IPlugin

class ServiceConfigPlugin(IPlugin):
   def __init__(self, parser=None, db=None, properties={}):
      self.is_preceeded_by = ['database']
      self.is_followed_by = ['servicecfg_database']
      self.parser = parser
      self.database = db
      self.properties = properties

   def install(self, ctx):
      schema = self.database.schema
      servicecfg = schema.servicecfg('s')

      table = schema.create_table(servicecfg)
      table.service_name(str)
      table.property_key(str)
      table.property_val(str)

      if (servicecfg._name not in self.database.get_tablenames()):
         tx = self.database.new_transaction()
         tx.execute(table)
         tx.commit()
         tx.close()
      else:
         print "table %s already exists.  not re-creating." % (servicecfg._name)

