



def _op(op, left, right):
    if not isinstance(right, SQLOperand):
        right = SQLLiteral(right)
    return SQLOperator(left, infix=op, second=right)

def _nullop(op, left):
    return SQLOperator(left, infix=op, second="NULL")
    
def _selfop(op, right):
    return SQLOperator(right, prefix=op, bracket=False)

def _desc(left):
    return SQLOperator(left, right, postfix="DESC", bracket=False)

def _and(left, right):
    return _op("AND", left, right)

def _or(left, right):
    return _op("OR", left, right)

def _padded(string):
    return (" %s " % (string)) if string else ""

literal_substitution = "?"



class SQLOperand:
    def __init__(self):
        pass

    def __eq__(self, other):
        if other is None:
            return _nullop('IS', self)
        return _op('=', self, other)

    def __ne__(self, other):
        if other is None:
            return _nullop('IS NOT', self)
        return _op("!=", self, other)

    def __not__(self, other):
        return _op("NOT", self, other)

    def __ge__(self, other):
        return _op(">=", self, other)

    def __le__(self, other):
        return _op("<=", self, other)

    def __lt__(self, other):
        return _op("<", self, other)

    def __gt__(self, other):
        return _op(">", self, other)

    def __add__(self, other):
        return _op("+", self, other)

    def __sub__(self, other):
        return _op("-", self, other)

    def __mul__(self, other):
        return _op("*", self, other)

    def __div__(self, other):
        return _op("/", self, other)

    def __mod__(self, other):
        return _op("%", self, other)

    def __and__(self, other):
        return _op("AND", self, other)

    def __or__(self, other):
        return _op("OR", self, other)

    def __xor__(self, other):
        return _op("XOR", self, other)

    def __invert__(self):
        return _selfop("NOT", self)

    def in_(self, other):
        return _op("IN", self, other)

    def like(self, other):
        return _op("LIKE", self, other)

    def desc(self):
        return _desc(self)

    def parameters(self, collection=[]):
        return collection

class SQLLiteral(SQLOperand):
    def __init__(self, value):
        self._value = value
        
    def __str__(self):
        return literal_substitution
    
    def parameters(self, collection=[]):
        collection.append(self._value)
        return collection
    
class SQLOperator(SQLOperand):
    
    def __init__(self, first, second=None, prefix=None, infix=None, postfix=None, bracket=True):
        self._first = first
        self._second = second
        self._prefix = _padded(prefix)
        self._postfix = _padded(postfix)
        self._infix = _padded(infix)
        self._pattern = "(%s%s%s%s%s)" if bracket else "%s%s%s%s%s"

    def __str__(self):
        return  self._pattern % (self._prefix, self._first, self._infix, self._second, self._postfix)
    
    def parameters(self, collection=[]):
        if self._first:
            self._first.parameters(collection)
        if self._second and isinstance(self._second, SQLOperand):
            self._second.parameters(collection)
        return collection
            
class SQLPair:
    def __init__(self, name):
        self._name = name
        self._alias = None
        self._columns = None
    
    def __call__(self, alias):
        self._alias = alias
        return self
        
    def __getattr__(self, attr):
        return SQLTriple(self, attr)
    
    def __str__(self):
        return "%s %s" % (self._name, self._alias) if self._alias else self._name
    
    def __setattr__(self, key, value):
        if key.startswith("_"):
            self.__dict__[key] = value
            return
        if self._columns is None:
            self._columns = {}
        
        if not isinstance(value, SQLOperand):
            value = SQLLiteral(value)
            
        self._columns[key] = value

class SQLTriple(SQLOperand):
    def __init__(self, pair, attr):
        SQLOperand.__init__(self)
        self._pair = pair
        self._name = attr
        
    def __str__(self):
        return "%s.%s" % (str(self._pair._alias), str(self._name)) if self._pair._alias else self._name  


class Schema:
    
    def __init__(self, schema_name=""):
        self.name = schema_name
    
    def __getattr__(self, tablename):            
        return SQLPair("%s%s" % (self.name,tablename))
    
    def select(self, *columns):
        return SQLQuery(*columns)
    
    def insert_into(self, table):
        return SQLInsert().into(table)
    
    def create_table(self, table):
        return SQLCreateTable(table)
    
    def update(self, *tables):
        return SQLUpdate(*tables)

class SQLCommand:

    def __init__(self, command):
        self._tables = None
        self._command = command

    def _tables(self, *tables):
        self._tables = [(SQLPair(str(t)) if not isinstance(t, SQLPair) else t) for t in tables]
        return self
    
    def parameters(self, collection=[]):
        return collection

    def __str__(self):
        return self._command % self.__map__()

types_to_sqltypes = {
                     str : "VARCHAR(100)", 
                     int : "INTEGER",
                     bool: "BOOLEAN",
                     }

class SQLColumn:
    
    def __init__(self, name, type=str):
        self._name = name
        self._constraints = []
        self(type)
        
    def __call__(self, type):
        self._type = types_to_sqltypes.get(type)
        return self
        
    def constraint(self, constraint):
        self._constraints.append(constraint)
        return self
        
    def primary_key(self):
        return self.constraint("PRIMARY KEY")

    def foreign_key(self, key):
#        ref = "%s.%s" % (key._pair._name, key._name) if isinstance(key, SQLTriple) else str(key)
#        return self.constraint("FOREIGN KEY %s" % (ref))
        return self 
        
    def not_null(self):
        return self.constraint("NOT NULL")
        
    def auto_increment(self):
        return self.constraint("AUTOINCREMENT")
        
    def __map__(self):
        return {
                'type': str(self._type),
                'name': self._name,
                'constraints': " ".join(self._constraints)
                }
        
    def __str__(self):
        return "%(name)s %(type)s %(constraints)s" % self.__map__() 

class SQLCreateTable(SQLCommand):
    
    def __init__(self, table):
        SQLCommand.__init__(self, "CREATE TABLE %(table)s (\n\t%(columns)s\n\t%(constraints)s\n)")
        self._table = table
        self._columns = {}
        self._constraints = []
        self._ordered_columns = []

    def __getattr__(self, name):
        if self._columns.has_key(name):
            return self._columns[name]
        c = SQLColumn(name)
        self._columns[name] = c
        self._ordered_columns.append(c)
        return c
    
    
    def constraint(self, constraint):
        self._constraints.append(constraint)
        
    def primary_key(self, *keys):
        self.constraint("PRIMARY KEY (%s)" % (", ".join(keys)))
    
    def __map__(self):
        map = {
            'table' : self._table._name if isinstance(self._table, SQLPair) else str(self._table),
            'columns' : ",\n\t".join([str(c) for c in self._ordered_columns]),
            'constraints' : "\n\t".join(self._constraints)
                }
        return map

class SQLInsert(SQLCommand):
    # TODO: match the SQLInsert interface to the SQLUpdate
    
    def __init__(self):
        SQLCommand.__init__(self,  "INSERT INTO %(tables)s\n\t(%(columns)s)\n\tVALUES\n\t(%(literals)s)")
        self._insert = {}
        

    def into(self, table):
        return SQLCommand._tables(self, table)

    def __setattr__(self, key, value):
        if key.startswith('_'):
            self.__dict__[key] = value
        else:
            self._insert[key] = value
    
    def parameters(self, collection=[]):
        keys, values = self._all_columns()
        for v in values:
            if isinstance(v, SQLOperand):
                v.parameters(collection)
            else:
                collection.append(v)
        return collection

    def __map__(self):
        
        keys, values = self._all_columns()
        
        return { 'tables' : str(self._tables[0]._name),
               'literals' : ", ".join([literal_substitution for v in values]),
               'columns' : ", ".join([str(k._name) for k in keys])
               }
        
    def _all_columns(self):
        keys = []
        values = []
        for table in self._tables:
            if table._columns:
                for c in table._columns.items():
                    keys.append(SQLTriple(table, c[0]))
                    values.append(c[1])
            
        return keys, values

        
class SQLUpdate(SQLInsert):

    def __init__(self, *tables):
        SQLInsert.__init__(self)
        SQLCommand.__init__(self,"UPDATE %(tables)s\n\tSET %(columns)s %(where)s %(postamble)s")
        self.tables(*tables)
        self._condition = None
        
    def tables(self, *tables):
        return SQLCommand._tables(self, *tables)

    def where(self, condition):
        self._condition = condition
        return self
    
    def parameters(self, collection=list()):
        keys, values = self._all_columns()
        
        for v in values:
            if isinstance(v, SQLOperand):
                v.parameters(collection)
            else:
                collection.append(v)
        
        if self._condition and isinstance(self._condition, SQLOperand):
            self._condition.parameters(collection)

        return collection

    def _all_columns(self):
        keys = []
        values = []
        for table in self._tables:
            if table._columns:
                for c in table._columns.items():
                    keys.append(SQLTriple(table, c[0]))
                    values.append(c[1])
            
        
        return keys, values

    def __map__(self):
        keys, values = self._all_columns()
        
        
        
        map = {}
        map['tables'] = ", ".join([str(s) for s in self._tables])
        map['columns'] = ", ".join(["%s = %s" % (str(k), str(v)) for (k, v) in zip(keys, values)])
        map['where'] = "\n\tWHERE %s" % (str(self._condition)) if self._condition else ""
        map['postamble'] = ""
        
        return map
        



class SQLQuery(SQLCommand):

    def __init__(self, *columns):
        SQLCommand.__init__(self, "SELECT %(columns)s FROM %(tables)s %(where)s %(postamble)s")
        self._where_ = "WHERE %(condition)s"
        self._condition = None
        self._postamble = ""
        self._columns = columns
        self._column_mask = "%s"
        

    def from_(self, *tables):
        return SQLCommand._tables(self, *tables)

    def where(self, condition):
        self._condition = condition
        return self
        
    def parameters(self, collection=[]):
        if self._condition:
            self._condition.parameters(collection) 
        return collection
    
    def max(self):
        self._column_mask = "MAX(%s)"
        return self
    
    def count(self):
        self._column_mask = "COUNT(%s)"
        return self
    
    def __map__(self):
        map = {'tables': ", ".join([str(t) for t in self._tables]), 'where': "", 'postamble': self._postamble}
        columns = []
        for c in self._columns:
            if isinstance(c, SQLPair):
                c = c.__getattr__('*')
            
            columns.append(str(c))
        
        col = ", ".join([str(t) for t in columns]) if len(columns) else "*"
        map['columns'] = self._column_mask % (col)
        if self._condition:
            map['condition'] = str(self._condition)
            map['where'] = self._where_ % {'condition': str(self._condition)}
        
        return map

    def _select_count(self):
        map = self.__map__()
        map['columns'] = "COUNT(*)"
        
        return self._command % map