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
        
        internal = InternalCommands(self.parser)
        ctx.er.message_patterns.add('^inspect', internal.inspect)
        ctx.er.message_patterns.add('^(?P<metadata_command>metadata)', internal.metadata_command)
        
        ctx.er.template_files.add(self, "ui/templates/introspection_commands.txt")
        ctx.er.phrase_banks.add(self, "ui/templates/zander_introspection_commands.txt")
        

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
        replies = self._help_text
        metadata['command'] = 'help_command'
        metadata['doc_strings'] = self._help_text

    def time(self, metadata):
        from datetime import datetime
        metadata['time'] = datetime.utcnow()
        metadata['command'] = 'time_command'
        

class InternalCommands:
    
    def __init__(self, parser=None):
        self.parser = parser
    
    def inspect(self, metadata):
        """inspect\t:- Display all micro-parsers in order"""
        replies = map(lambda s: s.id, self.parser.micro_parsers)
        metadata['parser_filters'] = replies
        metadata['parser_actions'] = [s.id for s in self.parser.actions]
        metadata['command'] = 'inspect_microparsers_command'

    def metadata_command(self, metadata):
        metadata['command'] = 'metadata_command'
        
        