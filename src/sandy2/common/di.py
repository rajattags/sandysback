
class Injector(object):

    """Primitive class to maintain a dictionary of things to be used in lieu of singleton objects. 
    
    For want of a better name, this may be thought of as a small dependency injector.
    
    Facilities exist for lazy instantiation of objects, as well as per instance instantiation.
    
    Instances of the object being configured are examined, and any attributes which can be set are. 

    e.g. 
        di = sandy2.di.Injector()
        
        # value is calculated now (no lambda needed)
        di.eager_singleton(properties_url = '/etc/sandy2/config.properties')
        di['operating_system'] = 'Linux'
        
        # value is calculated lazily. Only one instance is allowed.
        di.lazy_singleton(preferences_window = lambda : UserLogin())
        
        # value is calculated on a per instance basis
        di.per_instance(logger = lambda object : Logger(object.__class__))
        
        # Now call:
        
        object = MyObjectNeedingConfiguration()
        di.configure(object)
        
        # any of these values are available via:
        object.logger
        object.properties_url
        object.preferences_window
        
        # Alternatively, and more directly, they can be accessed more directly via:
        di['properties_url']
        di['logger']
        di['preferences_window']
    """
    
    def __init__(self, **initial_values):
        self.__dict = {}
        self.eager_singleton(**initial_values)
        
    
    def configure(self, obj):
        """Iterate through all attributes of the given object, and set them with values taken from the injector.
        """
        for key in obj.__dict__.keys():
            try:
                fn1 = self.__dict[key]             
                obj.__dict__[key] = self.__evaluate_function(key, obj)
            except KeyError:
                pass

    def __setitem__(self, key, item):
        if item is None:
            del self.__dict[key]
        else: 
            self.__register_lambda(key, lambda x : item)

    def __delitem__(self, key):
        del self.__dict[key]

    def __getitem__(self, key):
        return self.__evaluate_function(key)

    def get(self, key, default_value=None):
        return self.__getitem__(key) if self.__dict.has_key(key) else default_value

    def __register_lambda(self, key, fn):
        assert callable(fn)
        self.__dict[key] = fn

    def __evaluate_function(self, key, obj=None):
        """Attempt to call the given function with a single variable.
        If the function fails because it has too few arguments, the function call 
        is attempted again, but with no arguments.
        """
        fn1 = self.__dict[key]
        result, numArgs = self._call_0_or_1_args(fn1, obj)
        
        # it turns out what we thought was a single arg lambda is a zero arg lambda 
        
        if (numArgs == 0):
            fn0 = fn1
            # so, for efficiency, we should replace the zero arg one with a single arg one.
            fn1 =  lambda x : fn0()
            self.__dict[key] = fn1
        return result
        # of course, if this were a lambda with more than one argument, this isn't catered for here.
            
    def _call_0_or_1_args(self, fn, obj=None):
        # Private method to call a function with one or more args. Not sure if this is the best way of doing this.
        num =  fn.func_code.co_argcount
        if num == 0:
            return fn(), 0
        else:
            return fn(obj), 1
        
    
    def per_instance(self, **lambdas):
        """Register a function with a name, which will be evaluated everytime the named attribute is asked for.
        """
        for key, fn in lambdas.items():
            self.__register_lambda(key, fn)
    
    def eager_singleton(self, **values):
        """Register a value with a name, which is available the named attribute is asked for.
        """
        for k, v in values.items():
            self.__setitem__(k, v)
    
    def lazy_singleton(self, **lambdas):
        """Register a function with a name. The function is evaluated once, the first time the attributes is asked for. 
        
        On subsequent calls, the same value will be returned.
        """
        for key, fn in lambdas.items():
            self.__register_singleton(key, fn)

    def __register_singleton(self, key, create_instance):
        from threading import Lock
        class SingletonHolder(object):
            def __init__(self, fn, di):
                self.instance = None
                self.create = fn
                self.lock = Lock()
                self.di = di
            
            def get_instance(self, x=None):
                try:
                    self.lock.acquire()
                    if (self.instance == None):
                        self.instance, n = self.di._call_0_or_1_args(self.create)
                    return self.instance
                finally:
                    self.lock.release()
        assert callable(create_instance)
        self.__register_lambda(key, SingletonHolder(create_instance, self).get_instance)


