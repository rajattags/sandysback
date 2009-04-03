from sandy2.data.linqish import Schema, SQLOperand, SQLCommand, SQLQuery, SQLTriple
from threading import BoundedSemaphore

# for standard sql
import MySQLdb
dbmod = MySQLdb
_cursor_styles = ["Cursor", "SSCursor"]
_show_tables = "show tables"

class DB:
    
    
    
    def __init__(self, *args, **kw):
        self.schema = Schema()
        self._connection_factory = self._create_connection(*args, **kw)
        self._initial_tables = None
    
    def new_transaction(self):
        return Transaction(self.get_connection(), self.schema)

    def get_connection(self):
        # TODO make a connection pool
        return self._connection_factory.next()
        
    def _create_connection(self, *args, **kw):
        """Connect to a database."""
        while True:
            yield dbmod.connect(*args, **kw)
        
    def get_tablenames(self):
        if not self._initial_tables:
            tx = self.new_transaction()
            self._initial_tables = tx.get_tablenames()
        return self._initial_tables
        
class Transaction:
    
    def __init__(self, obj, schema):
        self._db_connection = obj
        self.schema = schema
        self._is_open = True
        
    def __new_cursor(self):

        # cursors doesn't exist in sqlite3 it seems.
        if hasattr(dbmod, "cursors"):
            for style in _cursor_styles:
                if hasattr(dbmod.cursors, style):
                    c = self._db_connection.cursor(getattr(dbmod.cursors, style))
                    if c: return c
         
        return self._db_connection.cursor()
        
    def execute(self, sql_command):
        params = []
        template = str(sql_command)
        if isinstance(sql_command, SQLCommand):
            params = sql_command.parameters([])
        
        results = Results(self.__new_cursor, sql_command, template, params)
        if isinstance(sql_command, SQLQuery):
            return results
        r = results._query(template, params)
        results._db_cursor.close()
        return r
    
    def commit(self):
        self._db_connection.commit()
        
    def rollback(self):
        self._db_connection.rollback()
        
    def close(self):
        if self._is_open:
            # TODO send back to the connection pool.
            self._is_open = False
            self._db_connection.close()
        
    
    def get_tablenames(self):
        """Return all tables.
        """
        cursor = self.__new_cursor()
        exit_code = cursor.execute(_show_tables)
        tablenames = [row[0] for row in cursor.fetchall()]
        cursor.close()
        self.close()
        return tablenames
    
    def next_id(self, column):
        # we should be a bit more careful about the harvesting
        # auto-incrementing
        if isinstance(column, SQLTriple):
            q = self.schema.select(column).max().from_(column._pair)
            results = self.execute(q)
            for r in results:
                mx = r[0]
                if mx is not None:
                    return mx + 1
            return 0
        else:
            raise TypeError("Must use an SQLTriple to specify a column")
    
class Results:

    def __init__(self, cursor_fn, sql_command, sql_string, params):
        self._db_cursor = None
        self._sql_command = sql_command
        self._sql_string = sql_string
        self._cursor_fn = cursor_fn
        self._params = params
        self._debug = True

    def __iter__(self):
        self._query(self._sql_string, self._params)
        return self

    def _query(self, query, params):
        if 1 or not self._db_cursor:
            self._db_cursor = self._cursor_fn()
        if dbmod.paramstyle is 'format':
            query = query.replace('?', '%s')
        if self._debug:
            print "Query: %s ; ==> %s" % (query, params)
        return self._db_cursor.execute(query, params)

    def next(self):
        r = self._db_cursor.fetchone()
        if not r:
            self._db_cursor.close()
            raise StopIteration
        return r
    
    def __getitem__(self, item):
        import types
        q = self._sql_string
        if isinstance(item, types.SliceType):
            q = q + " limit %s, %s" % (item.start, item.stop - item.start + 1)
            self._query(q, self._params)
            return self._db_cursor.fetchall()
        elif isinstance(item, types.IntType):
            if item < 0:  # add support for negative (from the end) indexing
                item = len(self) + item
                if item < 0:
                    raise IndexError, "index too negative"
            q = q + " limit %s, 1" % (item)
            self._query(q, [])
            return self._db_cursor.fetchone()
        else:
            raise IndexError, "unsupported index type"
        
    def __len__(self):
        q = self._sql_command._select_count()
        self._query(q, self._params)
        return int(self._db_cursor.fetchone()[0])