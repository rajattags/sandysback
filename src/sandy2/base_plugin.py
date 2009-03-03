from sandy2.common.parsing import IMicroParser, IMessageAction, Parser
from sandy2.common.plugins import IPlugin

class BasicMicroParsingPlugin(IPlugin):
    
    def __init__(self, parser=None):
        self.parser = parser
        
    def start_up(self):
        self.parser.add_micro_parser(TagExtractor())
        self.parser.add_micro_parser(TokenizerParser())

class TokenizerParser(IMicroParser):

    """Consumes: incoming_message"""
    """Produces: tokens, first_word"""

    def __init__(self):
        self.is_preceeded_by = ['head', 'incoming_message']
        self.is_followed_by = ['tokens', 'first_word']

    def micro_parse(self, metadata):
        tokens = map(lambda s: s.lower(), metadata['incoming_message'].strip().split(' '))
        metadata['tokens'] = tokens
        metadata['first_word'] = tokens[0]

class TagExtractor(IMicroParser):
    """Consumes: tokens"""
    """Produces: tags"""

    def __init__(self):
        self.is_preceeded_by = ['tokens']
        self.is_followed_by = ['tags', 'special_tags']

    def micro_parse(self, metadata):
        tags = filter(lambda s: s.startswith('#'), metadata['tokens'])
        metadata['tags'] = map(lambda s: s.strip('#'), tags)
        metadata['special_tags'] = list()
