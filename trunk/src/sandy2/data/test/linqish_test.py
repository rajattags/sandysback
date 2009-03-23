

import unittest
from sandy2.data.linqish import *

class LinqishTest(unittest.TestCase):
    
    def setUp(self):
        pass
    
    def testSQLPair(self):
        
        s = Schema()
        
        table = s.users
        self.assertFalse(table is None)
        self.assertEquals("users", str(table))
        
        table = s.users("u")
        self.assertFalse(table is None)
        self.assertEquals("users u", str(table))

    def testSQLTriple(self):
        
        s = Schema()
        
        table = s.users
        attr = table.email
        self.assertEquals("email", str(attr))
        
        table = s.users("u")
        self.assertEquals("u.email", str(table.email))

    def testSelect(self):
        
        s = Schema()
        
        p = s.pages("p")
        query = s.select(p).from_(p).where(p.title == 'index.html')

        self.assertEquals("SELECT p.* FROM pages p WHERE (p.title = ?) ", str(query))
        self.assertEquals(1, len(query.parameters()))

        print s.select(p.title).from_(p).where((p.author == None) | (p.license != None))
        
        p = s.pages("p")
        command = s.select(p.age).from_(p).max()

        
        
        print str(command)
        
        self.assertNotEquals(None, command)
        
        print command._select_count()
        
    def testUpdate(self):
        schema = Schema()
        
        p = schema.pages('p')
        a = schema.authors('a')
        
        q = schema.update(p, a).where(p.date >= 1000)
        p.title = "New Title"
        p.name = "Unknown"
        
        a.works = a.works + 1
        
        print q
        print q.parameters([])
        self.assertEquals(4, len(q.parameters([])))
        print q.parameters()
        
        users = schema.users("u")
        e = schema.email("e")
        
        e.is_verified = not e.is_verified
        e.email = 'unknown@blackhole.com'
        q = schema.update(e).where(e.is_verified != None)
        
        print q
    
    def testInsert(self):
        s = Schema()
        
        t = s.users("u")
        insert = s.insert_into(t)
        t.name = 'James'
        t.user_id = 2
        t.awesomeness = True
        
        print insert
        self.assertEquals(3, len(insert.parameters()))
        
    def testCreateTable(self):
        s = Schema()
        
        t = s.create_table(s.email('e'))
        t.email(str).primary_key().not_null()
        t.user_id(int).foreign_key(s.users.id)
        t.name.not_null()
        
        s = str(t)
        
        print t
        self.assertTrue(s.find('CREATE TABLE email') >= 0)
        
    
    def testConditional(self):
        
        s = Schema()
        
        u = s.users
        self.assertEquals("(username > ?)", str(u.username > "james"))

        u = s.users('u')
        self.assertEquals("(u.username > ?)", str(u.username > "james"))
        self.assertEquals("(u.username = ?)", str(u.username == "james"))
        
        

if __name__ == "__main__":
    unittest.main()