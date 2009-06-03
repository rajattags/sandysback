import re

def default_pattern_transform(pattern):
    return pattern.replace(" ", "[.:;?!\s]+").replace('^', '^\s*')

class REDispatcher:
    """Conditionally executes a callable, based upon the occurrence of a pattern in 
    a block of text."""
    def __init__(self, pattern_transformer=default_pattern_transform):
        """Constructor. An optional pattern transformer is allowed. Patterns transforms are 
        applied to all string patterns registered.
        The default pattern transform replaces all instances of whitespace with [.:;?!\s]+.
        """
        self._re_map = {}
        if not callable(pattern_transformer):
            pattern_transformer = None
        self.pattern_transformer = pattern_transformer
        
    def register_re(self, regexp, function):
        """Register a new regular expression object with a function to be fired when the pattern 
        is detected."""
        assert callable(function)
        assert hasattr(regexp, 'match')
        
        self._re_map[regexp] = function
        return regexp
        
    def register_pattern(self, pattern, function, flags=re.IGNORECASE | re.DOTALL | re.UNICODE):
        """Compile a regular expression from the given pattern, and register it to fire the given 
        function when the pattern is detected.
        
        The pattern transformer is used to transform the pattern before compilation. 
        The given flags are passed directly to the regular expression compilation.
        """
        if self.pattern_transformer:
            pattern = self.pattern_transformer(pattern)
        
        r = re.compile(pattern, flags)
        return self.register_re(r, function)
        

    def search(self, string, message=None):
        """Search the given string for any patterns registered with this object. 
        If any patterns are found, a) the match object is added to the object via an 
        optional add_dictionary() method, b) the function associated with the pattern is 
        executed."""
        if message is None:
            message = string
        matched = False
        for r, fn in self._re_map.items():
            m = r.search(string)
            if m:
                if hasattr(message, 'add_dictionary'):
                    match = m
                    message.add_dictionary(lambda key: match.groupdict()[key])
                    fn(message)
                else:
                    fn(m)
                matched = True
        return matched
    
    def _find_name(self, fn):
        if hasattr(fn, '__name__'):
            return fn.__name__
        elif hasattr(fn, 'im_self'):
            return _find_name(self, fn.im_self)
        
        return str(fn)