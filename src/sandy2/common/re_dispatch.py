import re

def default_pattern_transform(pattern):
    return pattern.replace(" ", "[.:;?!\s]+")  

class REDispatcher:
    
    def __init__(self, pattern_transformer=default_pattern_transform):
        self._re_map = {}
        if not callable(pattern_transformer):
            pattern_transformer = None
        self.pattern_transformer = pattern_transformer
        
    def register_re(self, regexp, function):
        assert callable(function)
        assert hasattr(regexp, 'match')
        
        self._re_map[regexp] = function
        return regexp
        
    def register_pattern(self, pattern, function, flags=re.IGNORECASE | re.DOTALL | re.UNICODE):
        if self.pattern_transformer:
            pattern = self.pattern_transformer(pattern)
        
        r = re.compile(pattern, flags)
        return self.register_re(r, function)
        

    def search(self, string, message=None):
        if not message:
            message = string
        matched = False
        for r, fn in self._re_map.items():
            m = r.search(string)
            if m:
                if hasattr(message, 'add_dictionary'):
                    message.add_dictionary(lambda key: m.group(key))
                    fn(message)
                else:
                    fn(m)
                matched = True
        return matched
