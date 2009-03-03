from sandy2.common.parsing import IMicroParser, IMessageAction, Parser
from sandy2.common.plugins import IPlugin

from string import join

class IntrospectionPlugin(IPlugin):
    
    def __init__(self, parser=None):
        self.parser = parser
        
    def start_up(self):
        self.parser.add_micro_parser(HelpCommand())
        self.parser.add_micro_parser(InspectCommand())
        self.parser.add_micro_parser(TimeCommand())
        self.parser.add_micro_parser(EchoCommand())
        self.parser.add_micro_parser(MetadataCommand())

    


class InspectCommand(IMicroParser):
    """Short description: Display all micro-parsers in order
    """
    """Consumes: tokens
    Produces: reply_message"""

    def __init__(self, parser=None):
        self.is_preceeded_by = ['first_word']
        self.is_followed_by = ['reply_message']
        self.parser = parser

    def micro_parse(self, metadata):
        first_word = metadata['first_word']
        if len(metadata['tokens']) > 1:
            second_word = metadata['tokens'][1]
        else:
            second_word = 'all'

        if first_word in ['inspect']:
            replies = map(lambda s: s.id, self.parser.micro_parsers)
            msg = "Parsers:\n\t-> " +join(replies, " \n\t-> ")
            metadata['reply_message'] = msg
            metadata['reminder_message'] = msg  

class MetadataCommand(IMicroParser):
    def __init__(self):
        self.is_preceeded_by = ['first_word', 'output_message']
        self.is_followed_by = []

    def micro_parse(self, metadata):
        first_word = metadata['first_word']
        if first_word == 'metadata':
            m = "\n".join(map(lambda (k,v): "%s%s: %s" % (k, " " * (25 - len(k)), v), metadata.items()))
            metadata['reply_message'] = m
            metadata['reminder_message'] = m
            metadata['output_message'] = m
            

class HelpCommand(IMicroParser):
    """Short description: illustrative, but useless command
    """
    """Long description : """
    """Consumes: tokens, user"""
    """Produces: reply_message"""

    def __init__(self, parser=None):
        self.is_preceeded_by = ['first_word']
        self.is_followed_by = ['reply_message']
        self.parser = parser

    def micro_parse(self, metadata):
        first_word = metadata['first_word']
        if first_word in ['help', 'h', '?']:
            mp = filter(lambda mp: mp.__doc__, self.parser.micro_parsers)
            replies = filter(lambda s: s.find("Short description") >= 0, map(lambda s: "".join((s.id, ":\n\t\t\t", s.__doc__)), mp))
            msg = "Available commands:\n\t-> " +join(replies, " \n\t-> ")
            metadata['reply_message'] = msg
            metadata['reminder_message'] = msg

class TimeCommand(IMicroParser):

    """Short description: Timing command"""
    def __init__(self):
        self.is_preceeded_by = ['first_word']
        self.is_followed_by = ['reply_message', 'reminder_message']

    def micro_parse(self, metadata):
        from datetime import datetime
        first_word = metadata['first_word']
        if first_word in ['time', 'date']:
            msg = str(datetime.now())
            metadata['reply_message'] = msg
            metadata['reminder_message'] = msg

class EchoCommand(IMicroParser):
    """Short description: echos exactly what was typed.
    """
    def __init__(self):
        self.is_preceeded_by = ['incoming_message', 'first_word']
        self.is_followed_by = ['reply_message', 'reminder_message']

    def micro_parse(self, metadata):
        first_word = metadata['first_word']
        if first_word in ['echo']:
            metadata['reply_message'] = metadata['incoming_message']
            metadata['reminder_message'] = metadata['incoming_message']
            