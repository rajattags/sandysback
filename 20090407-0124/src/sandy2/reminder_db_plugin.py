from sandy2.common.parsing import IMicroParser, IMessageAction, Parser
from sandy2.common.scheduling import Scheduler, IJobStore, _s_to_dt
from sandy2.common.plugins import IPlugin


from sandy2.data.linqish import SQLPair

_STATUS_SCHEDULED = 0
_STATUS_TIME_IS_NOW = 1
_STATUS_HANDLED = 2

class SchedulerDBPlugin(IPlugin):

    def __init__(self, db=None, parser=None):
        self.is_preceeded_by = ['scheduling']
        self.database = db
        self.parser = parser
        self.scheduler = None
        self.properties = None

    def install(self):

        
        tx = self.database.new_transaction()
        schema = self.database.schema
        
        me = schema.message_event('me')
        if (me._name not in self.database.get_tablenames()):
            table = schema.create_table(me)
            table.message_id(int).foreign_key(schema.message.id)
            table.time_to_fire(float)
            table.handled(bool)
        
            tx = self.database.new_transaction()
            tx.execute(table)
            tx.commit()
            tx.close()
        else:
            print "Table %s already exists. Not re-creating." % (me._name)


        store = JobStoreDB()

        self.properties['configure'](store)
        self.scheduler.job_store = store
        
    
    def start_up(self):
        self.scheduler.start()
        pass 

class JobStoreDB(IJobStore):
    
    def __init__(self, database=None, table=None):
        self.database = database
        self.table = table

    def store_job(self, abs_seconds, message_id, message, medium, user_id):
        
        tx = self.database.new_transaction()
        
        s = tx.schema
        me = s.message_event('me')
        me.message_id = message_id
        me.time_to_fire = abs_seconds
        me.handled = _STATUS_SCHEDULED
        
        tx.execute(s.insert_into(me))
        tx.commit()
        tx.close()
        pass
    
    def find_ready_jobs(self, now):
        tx = self.database.new_transaction()
        
        s = tx.schema
        m = s.message('m')
        me = s.message_event('me')
        
        me.handled = _STATUS_TIME_IS_NOW
        update_query = s.update(me).where((me.time_to_fire <= now) &
                                     (me.handled == _STATUS_SCHEDULED))
        tx.execute(update_query)
        tx.commit()
        
        query = s.select(m.id, m.text, m.user_id, m.input_medium, me.time_to_fire).\
                   from_(m, me).\
                   where(
                         (m.id == me.message_id) & 
                         (me.handled == _STATUS_TIME_IS_NOW)
                         )
        jobs = tx.execute(query)
        
        for (message_id, message, user, medium,  time_to_fire) in jobs:
            row = (message_id, message, medium, user)
            yield (time_to_fire, row, dict())
            me.handled = _STATUS_HANDLED
            tx.execute(s.update(me).where(me.message_id == message_id))
        
        # not sure if the update should be committed on each iteration..
        tx.commit()
        tx.close()
        
    def start(self):
        tx = self.database.new_transaction()
        s = tx.schema
        me = s.message_event('me')
        me.handled = _STATUS_SCHEDULED
        tx.execute(s.update(me).where(me.handled == _STATUS_TIME_IS_NOW))
        tx.commit()
        tx.close()
    
    def find_next_earliest_time(self):
        tx = self.database.new_transaction()
        s = tx.schema
        me = s.message_event('me')
        rows = tx.execute(s.select(me.time_to_fire).min().
                            from_(me).
                            where(
                                  (me.handled == _STATUS_SCHEDULED))
                            )
        
        for r in rows:
            return r[0]
        return None

    def __str__(self):
        tx = self.database.new_transaction()
        me = tx.schema.message_event('me')
        m = tx.schema.message('m')
        query = tx.schema.select(me.handled, me.time_to_fire, m.text).from_(m, me).where(
                                                                          (m.id == me.message_id) &
                                                                          (me.handled != _STATUS_HANDLED)
                                                                          ).order_by(me.time_to_fire).ascending()                    
        return "\n".join(["\t%s at %s: '%s'" % (st, _s_to_dt(s), text.strip()) for (st, s, text) in tx.execute(query)])