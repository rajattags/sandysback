#!/usr/bin/python

from string import join

# Modify the following to support other databases:
import sqlite3

dbmod = sqlite3
# for standard sql
# get_tables = "show tables"  # how to get a list of tables
# for sqlite3
get_tables = "SELECT name FROM sqlite_master WHERE type = 'table'"

import types

# Based upon code/article from http://www.devx.com/dbzone/Article/22093/1954
# updated for
# a) to use SQLite3
# b) use the safer Prepared statement form, instead of rolling our own where clauses.
# c) changed some method names to make them look a bit more linq'ish
# d) added a create table method.

class Table:
    """Emulates a list of DB rows, where each row is a tuple.
        May also be accessed via a string, to pull entire columns.
        Examples:
            t = Table(db, "users")
            ### select and organize data
            t.search("id<100")
            t.search("id<?", 100)
            t.sort("lastname, firstname")
            ### retrieve data
            rows = t[3:12]   # get 9 records, from the 4th to the 12th
            record = t[-5]   # get the 5th record from the end
            names = t["firstname, lastname"]  # return a list of all firstname-lastname tuples
            ### iterate over data
            for row in t:  print row
            ### add data
            t.insert('', 'Bob', 'Barker', 'bbarker')
            ### remove data (unconfirmed)
            del t[58]
            
            rows = db.From("users").\
                        select("lastname", "firstname").\
                        where("id < ? and age > ?", 100, 18).\
                        order_by("lastname asc")
            
            for row in rows:
                print row
                
            #### simple joins.
            rows = dm.From("users u", "email e").\
                        select("u.nickname", "e.email").\
                        where("u.id == ?", id)
            
                        
    """
    def __init__(self, db, *tables):
        self.db = db
        self.name = join(tables, ', ')
        self.db_cursor = None
        self._debug = True
        self._styles = ["Cursor", "SSCursor"]
        self._sort = ""
        self._search = ""
        self._columns = "*"
        self._where_params = ()
        self.__id_generators = {}

    def sort(self, method):
        """Alternative spelling of order_by
        """
        self._sort = ""
        if method: self._sort = "order by %s" % (method)
        return self

    def order_by(self, method):
        """Add an ORDER BY clause to a SELECT statement.
        """
    	return self.sort(method)

    def search(self, method, *values):
        """Alternative spelling to where method
        """
        self._search = ""
        if method: 
        	self._search = "where %s" % (method)
        	self._where_params = values
        
        return self

    def where(self, method, *values):
        """Add a WHERE clause to a SELECT statement.
        """
    	return self.search(method, *values)

    def select(self, *columns):
        """Specify the columns selected. This is strongly advised, since rows that are outputted are tuples, 
        of indeterminate order.
        
        If no arguments are specified, then "*" is used.
        """
    	if len(columns) > 0:
    	    self._columns = join(columns, ', ')
    	else: 
    		self._columns = '*'
    	return self

    def __new_cursor(self):
        "ensure we have a fresh, working cursor.  (improves support for SSCursors)"
        if self.db_cursor:
            self.db_cursor.close()
        # cursors doesn't exist in sqlite3 it seems.
        if hasattr(dbmod, "cursors"):
            for style in self._styles:
                if hasattr(dbmod.cursors, style):
                    print style
                    self.db_cursor = self.db.obj.cursor(getattr(dbmod.cursors, style))
                    break
        else: 
            self.db_cursor = self.db.obj.cursor()

    def __query(self, q, data=None):
        if not self.db_cursor:
            self.__new_cursor()
        if self._debug:
            print "Query: %s ; ==> %s" % (q, data)
         
        return self.db_cursor.execute(q, data)

    def __getitem__(self, item):
        q = "select %s from %s %s %s" % (self._columns, self.name, self._search, self._sort)
        if isinstance(item, types.SliceType):
            q = q + " limit %s, %s" % (item.start, item.stop - item.start)
            self.__query(q, self._where_params)
            return self.db_cursor.fetchall()
        elif isinstance(item, types.StringType):
            q = "select %s from %s %s %s" % (item, self.name, self._search, self._sort)
            self.__query(q, self._where_params)
            return self.db_cursor.fetchall()
        elif isinstance(item, types.IntType):
            if item < 0:  # add support for negative (from the end) indexing
                item = len(self) + item
                if item < 0:
                    raise IndexError, "index too negative"
            q = q + " limit %s, 1" % (item)
            self.__query(q)
            return self.db_cursor.fetchone()
        else:
            raise IndexError, "unsupported index type"

    def __setitem__(self, key, value):
        "Not yet implemented."
        # TODO can this use an UPDATE?
        if isinstance(key, types.IntType):
            pass
        else:
            raise IndexError, "index not a number"

    def __delitem__(self, key):
        # this method doesn't appear to be being called.
        q = "delete from %s %s" % (self.name, self._search)
        if isinstance(key, types.StringType):
            q = "delete from %s %s" % (self.name, self._search)
            if key is not '*':
            	if len(self._where_params) == 0:
				    q = q + ' where %s ' % (key)
            	else: 
            		q = q + ' and %s' % (key)
            
            	
            self.__query(q, self._where_params)
            
        elif isinstance(key, types.IntType):
            if key < 0:  # add support for negative (from the end) indexing
                key = len(self) + key
                if key < 0:
                    raise IndexError, "index too negative"
            q = q + " limit %s, 1" % (key)
            self.__query(q, self._where_params)
        

    def insert(self, *row):
        """Insert a single row into the given table.
        """
        fmt = ("?," * len(row))[:-1]
        q = "insert into %s values (%s)" % (self.name, fmt)
        self.__query(q, row)
        return self.db_cursor.fetchone()

    def __iter__(self):
        self.__new_cursor()
        q = "select %s from %s %s %s" % (self._columns, self.name, self._search, self._sort)
        self.__query(q, self._where_params)
        return self

    def next(self):
        r = self.db_cursor.fetchone()
        if not r:
            self.__new_cursor()
            raise StopIteration
        return r

    def __len__(self):
        self.__query("select count(*) from %s %s" % (self.name, self._search), self._where_params)
        r = int(self.db_cursor.fetchone()[0])
        return r

    def id(self, col=''):
        g = self.__id_generators.setdefault(col, self.__sequence_generator(col))
        return g.next()

    def __sequence_generator(self, col):
        
        currentmax = self.select('max(%s)' % (col))
        currentmax = currentmax[0] if len(currentmax) else 0
        print "currentmax is %s" % (currentmax) 
        while True:
            yield currentmax
            currentmax += 1

class DB:
    """
    A basic wrapper for databases.  Usage is as follows:
        d = db(user="user", passwd="password", db="database")
        table_name = d.tables()[0]
        t = d.table(table_name)
    The parameters for connect() and __init__() are keyword arguments, given
    directly to your database module.

    If you access the same table from several places in your code, there is no
    need to pass the table object around.  This class will keep track of them
    for you and provide the existing copy of a table, if one already exists.
    """
    def __init__(self, *args, **kw):
    	self.debug = True
        self._tables = {}
        if args:
            self.connect(*args, **kw)

    def tables(self):
        """Return all tables.
        """
        q = get_tables
        c = self.obj.cursor()
        a = c.execute(q)
        ts = []
        for row in c.fetchall():
            #print row
            ts.append(row[0])

        return ts

    def table(self, name):
    	"""Return a single table. If a table already exists, then return the pre-existing one.
    	"""
        try:
            return self._tables[name]
        except:
        	
            table =  self.from_(name)
            table._debug = self.debug
            self._tables[name] = table
            
            return self._tables[name]
    
    def into(self, name):
        return self.table(name)
    
    def from_(self, *tables):
        """Access one or more tables."""
    	return Table(self, *tables)
        
    def create_table(self, tablename, *cols):
        """Create and return a new table.
        
        The table columns must be an ordered list or tuple which will be passed directly to a CREATE TABLE statement.
        """
        query = "create table %s (%s)" % (tablename, join(cols, ', '))  
        if (self.debug):
        	print query
        self.obj.cursor().execute(query)
        return self.table(tablename)
        
        

    def connect(self, *args, **kw):
        """Connect to a database."""
        self.obj = dbmod.connect(*args, **kw)

if __name__ == "__main__":
    print "This file should not be executed"