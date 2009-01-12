import unittest
from sandy2.sqlobject import DB, Table


class DBTest(unittest.TestCase):

    def setUp(self):
        # conxStr = 'DRIVER=SQLite3 ODBC Driver;Database=sqllite.db;LongNames=0;Timeout=1000;NoTXN=0;SyncPragma=NORMAL;StepAPI=0;'
        dbPath = ":memory:"
        self.db = DB(dbPath)
        self.db.debug = False

        userTable = self.db.create_table('users', 'id integer', 'name text', 'nickname text')
                
        userTable.insert(0, 'Amy', 'amy')
        userTable.insert(1, 'William', 'bill')
        userTable.insert(2, 'Charles', 'charlie')
        userTable.insert(3, 'Denise', 'denise')
        

    def tearDown(self):
        # nop
        return

    def testCreateTable(self):
        userTable = self.db.table('users')
        self.assertTrue(userTable is not None)
        
        self.assertEquals(1, len(self.db.tables()))
        self.assertEquals(4, len(userTable))


    def testSimpleSelect(self):        
        
        # hardcoded id limit
        allusers = self.db.From('users').where('id >= 1')['id, name']
        self.printList(allusers)
        self.assertEquals(3, len(allusers))
        
        # variable substitution.
        allusers = self.db.From('users u').select('u.id', 'u.nickname', 'u.name').where("u.id >= ?", 2).order_by('u.name asc')
        self.printList(allusers)
        self.assertEquals(2, len(allusers))
        
        # deletion
        allusers = self.db.From('users').where('id > 0')['id, name']
        # this doesn't actually delete anything from the database
        del allusers[0:2]
        self.printList(allusers)
        self.assertEquals(1, len(allusers))
        

        allusers = self.db.From('users')
        print str(allusers)
        self.printList(allusers)
        self.assertEquals(4, len(allusers))

    def printList(self, allusers):
        for user in allusers:
            print str(user)


    def testSimpleJoin(self):
        table = self.db.create_table('email', 'user_id integer', 'email text')
        self.assertEquals(2, len(self.db.tables()))
        table.insert(0, 'amy@sandy.com')
        table.insert(1, 'william@butler-yates.org')
        table.insert(2, 'charles@petzold.us')
        
        allusers = self.db.From('users u', 'email e').select('u.nickname', 'e.email').where('u.id = e.user_id')
        self.printList(allusers)
        self.assertEquals(3, len(allusers))

__author__ = "james"
__date__ = "$06-Jan-2009 23:48:43$"

if __name__ == "__main__":
    unittest.main()