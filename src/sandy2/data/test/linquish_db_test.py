

import unittest
from sandy2.data.linqish_db import *
from sandy2.data.linqish import Schema

class LinqishDBTest(unittest.TestCase):

    def setUp(self):
        self.db = DB(user="root", passwd="MySQL-root-0", db="zander_test_database", host="127.0.0.1", port=3306)

        self.t = self.db.new_transaction()
        self.max_id = self.findMaxID()
        print "Max ID = ", self.max_id

    def tearDown(self):
        self.t.close()
        self.t = None

    def testCreateTable(self):
        pass
    
    def testSelect(self):
        schema = Schema()
        u = schema.user("u")
        
        
        query = schema.select(u).from_(u)
        
        print query
        
        results = self.t.execute(query)
        for r in results:
            print r
        slice = results[2:5]
#        self.assertEquals(3, len(slice))
        self.assertTrue(len(results))
        
        u = schema.user("u")
        e = schema.email('e')
        query = schema.select(u.fullname, e.email).from_(u, e).where((u.id == e.user_id) & (u.reminder_medium == 'email'))
        results = self.t.execute(query)
        for r in results:
            print r
            
        
    def findMaxID(self):
        s = Schema()
        u = s.user
        q = s.select(u.id).max().from_(u)
        
        results = self.t.execute(q)
        for r in results:
            return r[0]
        
    def testUpdate(self):
        schema = Schema()
        u = schema.user('u')
        
        query = schema.update(u).where(u.reminder_medium == None)
        u.reminder_medium = "email"
        
        print "Rows affected = %s" % (self.t.execute(query))
        
        
    def testInsert(self):
        schema = Schema()
        u = schema.user('u')
        
        query = schema.insert_into(u)
        
        u.id = self.max_id + 1
        u.fullname = 'Seamus Hugman'
        u.reminder_medium = "email"
        
        print query
        
        results = self.t.execute(query)
        
        print "Insert results = " + str(results)
        
        
        
        pass

if __name__ == "__main__":
    unittest.main()