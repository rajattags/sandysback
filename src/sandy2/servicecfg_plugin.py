from sandy2.common.plugins import IPlugin

from sandy2.transports.registration import AccountRegistrationListener

class ServiceConfigPlugin(IPlugin):
    def __init__(self, parser=None, db=None, properties={}):
        self.is_preceeded_by = ['database', 'passwords']
        self.is_followed_by = ['servicecfg_database']
        self.parser = parser
        self.database = db
        self.properties = properties
        self._account_registration = None
      

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

    def start_up(self, ctx):
        ar = AccountRegistrationListener()
        
        ctx.di.configure(ar)
        ctx.er.account_registration.track(ar.add_rule)
        
        self._account_registration = ar
    
    def run(self):
        print "Running polling on account registration email account %s" % (self._account_registration.registration_username)
        self._account_registration.run()
    
    def stop(self):
        if self._account_registration:
            self._account_registration.close()