
_NOT_PRESENT = "__not__present___"


class Message:
    """Extendable dictionary class.
    
    Instances can be extended in a number of ways:
    * key value pairs via standard dictionary access
    * setting attributes on the instance.
    * adding other dictionaries via the add_dictionary method.
    
    The latter mechanism allows the getitem method to scan the main dictionary for a key, followed 
    by any added dictionaries, until an entry can be found.
    """
    
    def __init__(self, metadata):
        self._metadata = metadata
        self._non_message = {}
        self._getters = []
        
    def __setitem__(self, key, value):
        """Set a value on the appropriate key. This will override any pre-existing entry, even on added dictionaries."""
        self._metadata[key] = value
    
    def __getitem__(self, key):
        """Scan available dictionaries looking for an entry with the given key. If none is found, a KeyError is raised."""
        value = self.get(key, _NOT_PRESENT)
        if value is not _NOT_PRESENT:
            return value
        raise KeyError(key)
        
    def has_key(self, key):
        """Returns true iff an entry is found in any dictionary with the given key."""
        return self.get(key, _NOT_PRESENT) != _NOT_PRESENT
    
    def get(self, key, default=None):
        """Scan available dictionaries looking for an entry with the given key. If none is found the default is returned.
        The default value for the default is None."""
        if self._metadata.has_key(key):
            return self._metadata[key]
        for getter in self._getters:
            try:
                return getter(key)
            except KeyError:
                pass
        return default
    
    def __setattr__(self, key, value):
        if key.startswith('_'):
            self.__dict__[key] = value
        else:
            self._non_message[key] = value
            
    def __getattr__(self, key):
        if key.startswith('_'):
            return self.__dict__[key]
        else:
            return self._non_message[key]
        
    def items(self):
        """Returns the items for the top level dictionary."""
        return self._non_message.items()
        
    def setdefault(self, key, default):
        return self._metadata.setdefault(key, default)
    
    def add_dictionary(self, new_map):
        """Accepts an object with the __getitem__ method, to extend this instance. This affects the getitem methods."""
        if callable(new_map):
            self._getters.append(new_map)
        elif hasattr(new_map, '__getitem__'):
            self._getters.append(new_map.__getitem__)

    def __str__(self):
        return self._non_message.__str__()