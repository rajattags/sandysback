from sandy2.common.parsing import IMicroParser, IMessageAction, Parser
from sandy2.common.plugins import IPlugin
from sandy2.common import NOP

from string import join

class IntrospectionPlugin(IPlugin):
    
    def __init__(self, parser=None):
        self.parser = parser
        
    def start_up(self, ctx):
        commands = Commands(self.parser)
        ctx.er.message_patterns.track(commands.help_text)
        ctx.er.help_text.track(commands.help_text_string)

        ctx.er.message_patterns.add('^time', commands.time)
        ctx.er.message_patterns.add('^(help|h\s*$|\?\s*$|hello)', commands.help)
        ctx.er.message_patterns.add('^(remind( me)?|r|echo) (?P<reminder_text>.*)', commands.remind_me)
        
        internal = InternalCommands(self.parser)
        ctx.er.message_patterns.add('^inspect', internal.inspect)
        ctx.er.message_patterns.add('^(?P<metadata_command>metadata)', NOP)
        ctx.er.micro_parsers.add(MetadataCommand())


        

class MetadataCommand(IMicroParser):
    def __init__(self):
        self.is_preceeded_by = ['first_word', 'output_message']
        self.is_followed_by = []

    def micro_parse(self, metadata):        
        if metadata.get('metadata_command', None):
            m = "\n".join(map(lambda (k,v): "%s%s: %s" % (k, " " * (25 - len(k)), v), metadata._metadata.items()))
            metadata['reply_message'] = m
            metadata['reminder_message'] = m
            metadata['output_message'] = m
            

class Commands:

    def __init__(self, parser=None):
        self.parser = parser
        self._help_text = []

    def help_text(self, pattern, fn):
        text = fn.__doc__
        if text:
            self.help_text_string("%s" % (text))

    def help_text_string(self, text):        
        self._help_text.append(text)

    def help(self, metadata):
        """hello, help, h, ?\t:- Gives this message."""
        """Long description : """
        """Consumes: tokens, user"""
        """Produces: reply_message"""
        mp = filter(lambda mp: mp.__doc__, self.parser.micro_parsers)
        prefix = ":- "
#        replies = filter(lambda s: s.find(prefix) >= 0, (s.__doc__ for s in mp))
        replies = self._help_text
        msg = "Available commands:\n\t-> " +join(replies, " \n\t-> ")
        metadata['reply_message'] = msg
        metadata['reminder_message'] = msg

    def time(self, metadata):
        from datetime import datetime
        msg = str(datetime.utcnow())
        metadata['reply_message'] = msg
        metadata['reminder_message'] = msg


    def remind_me(self, metadata):    
        """remind, r <something> <time>:- I'll remind you of <something> at a specific time. 
                e.g. remind me to pack my SICP book 8am tomorrow.
                e.g. remind me to move the car in 10 minutes
        """
        metadata['reply_message'] = metadata['reminder_text']
        metadata['reminder_message'] = metadata['reminder_text']

class InternalCommands:
    
    def __init__(self, parser=None):
        self.parser = parser
    
    def inspect(self, metadata):
        """inspect\t:- Display all micro-parsers in order"""
        """Consumes: tokens
        Produces: reply_message"""
        replies = map(lambda s: s.id, self.parser.micro_parsers)
        msg = "Parsers:\n\t-> " +join(replies, " \n\t-> ")
        metadata['reply_message'] = msg
        metadata['reminder_message'] = msg  
            