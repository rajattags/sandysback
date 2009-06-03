from sandy2.common.ordering import topological_sort, INode, DependencyList

""" The main parsing module. This really is just a scaffold around micro-parsers
and actions supplied externally.
"""


class Parser(object):

    def __init__(self, micro_parsers=[], actions=[], configure=None):
        self.actions = DependencyList(actions, configure)
        self.micro_parsers = DependencyList(micro_parsers, configure)
        self.debug = False

    def parse_message(self, message):
        return self.parse({"incoming_message": message, "input_medium": "stdin"})

    def parse(self, metadata):
        """Parse the message contained in the metadata.

        Metadata can include data other than the message, which may be
        considered by microparsers.

        No restriction is made upon exactly what processing is done in the
        micro-parsers: for example this may be simple pattern matching,
        parts-of-speech tagging, or a context free grammar parser.
        """

        metadata = Message(metadata)
        for t in self.micro_parsers:
            try:
                if getattr(t, 'micro_parse', None):
                    t.micro_parse(metadata)
            except BaseException, e:
                print "Exception %s: in %s" % (e, t)
            

        for t in reversed(self.micro_parsers._nodes):
            try:
                if getattr(t, 'cleanup', None):
                    t.cleanup(metadata)
            except BaseException, e:
                print "Exception %s: in %s" % (e, t)
        

        return metadata

    def __can_continue(self, metadata):
        """The STOP key should be used to prematurely terminate processing of a 
        command. 
        
        This would probably be useful for micro-parsers or commands that call 
        the parser recursively.
        """
        return metadata.get('STOP', None) is None

    def perform_actions(self, metadata):
        """Perform the actions in the order they were registered.
        """

        for a in self.actions:
            if self.__can_continue(metadata):
                # todo: check that this method actually exists.
                a.perform_action(metadata)
            else:
                break

    def add_micro_parser(self, new_parser):
        self.micro_parsers.append(new_parser)
        self.__ordered = False

    def add_action(self, new_action):
        self.actions.append(new_action)


class IMicroParser(INode):

    """An interface to let plugins help with parsing"""

    def micro_parse(self, metadata):
        """The single method can add or remove entries to the metadata dictionary.

        MicroParsers may cooperate with one another, or with other actions.
        """

    def cleanup(self, metadata):
        """Executed after all micro_parse methods have been executed, in the reverse order 
        of execution.        
        """

class IMessageAction(INode):

    """An interface to let plugins add extra actions to the parser."""

    def perform_action(self, metadata):
        """This single method should perform any action that should occur after all parsing has completed."""

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