import unittest
from attic.sqlobject import DB, Table


class DBTest(unittest.TestCase):

    def create_email_table(self):
        table = self.db.create_table('email', 'user_id integer', 'email varchar(100)')
        self.assertEquals(2, len(self.db.tables()))
        table.insert(0, 'amy@sandy.com')
        table.insert(1, 'william@butler-yates.org')
        table.insert(2, 'charles@petzold.us')
        self.db.drop_table('email')


    def setUp(self):
        # conxStr = 'DRIVER=SQLite3 ODBC Driver;Database=sqllite.db;LongNames=0;Timeout=1000;NoTXN=0;SyncPragma=NORMAL;StepAPI=0;'
        dbPath = ":memory:"
#        self.db = DB(dbPath)
        self.db = DB(user="root", passwd="MySQL-root-0", db="zander_test_database", host="127.0.0.1", port=3306)
        self.db.debug = False

        try:
            self.db.drop_table('users')
        except: 
            # table doesn't exist
            pass
        userTable = self.db.create_table('users', 'id integer', 'name varchar(100)', 'nickname varchar(100)')
        userTable.insert(0, 'Amy', 'amy')
        userTable.insert(1, 'William', 'bill')
        userTable.insert(2, 'Charles', 'charlie')
        userTable.insert(3, 'Denise', 'denise')
        

    def tearDown(self):
        self.db.drop_table("users")

    def testCreateTable(self):
        userTable = self.db.table('users')
        self.assertTrue(userTable is not None)
        
        self.assertEquals(1, len(self.db.tables()))
        self.assertEquals(4, len(userTable))


    def testSimpleSelect(self):        
        
        # hardcoded id limit
        allusers = self.db.from_('users').where('id >= 1')['id, name']
        self.printList(allusers)
        self.assertEquals(3, len(allusers))
        
        # variable substitution.
        allusers = self.db.from_('users u').select('u.id', 'u.nickname', 'u.name').where("u.id >= ?", 2).order_by('u.name asc')
        self.printList(allusers)
        self.assertEquals(2, len(allusers))
        
        # deletion
        allusers = self.db.from_('users').where('id > 0')['id, name']
        # this doesn't actually delete anything from the database
        del allusers[0:2]
        self.printList(allusers)
        self.assertEquals(1, len(allusers))
        

        allusers = self.db.from_('users')
        print str(allusers)
        self.printList(allusers)
        self.assertEquals(4, len(allusers))

    def printList(self, allusers):
        for user in allusers:
            print str(user)


    def testAutoIncrement(self):
        t = self.db.create_table('widgets', 'id integer primary key', 'name varchar(100)')
        id = t.insert(t.id(), 'w1')
        id = t.insert(t.id(), 'w2')
        self.printList(self.db.from_('widgets'))
        self.db.drop_table('widgets')

    def testSimpleJoin(self):
        self.create_email_table()
        allusers = self.db.from_('users u', 'email e').select('u.nickname', 'e.email').where('u.id = e.user_id')
        self.printList(allusers)
        self.assertEquals(3, len(allusers))
        
    def testParameterizedJoin(self):
        self.create_email_table()
        amyusers = self.db.from_('users u', 'email e').select('u.nickname', 'e.email').where('u.id = e.user_id and e.email = ?', 'amy@sandy.com')
        self.printList(amyusers)
        self.assertEquals(1, len(amyusers))
        

__author__ = "james"
__date__ = "$06-Jan-2009 23:48:43$"

if __name__ == "__main__":
    unittest.main()