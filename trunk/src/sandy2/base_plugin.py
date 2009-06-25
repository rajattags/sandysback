from sandy2.common.parsing import IMicroParser, IMessageAction, Parser
from sandy2.common.plugins import IPlugin
from sandy2.common.re_dispatch import REDispatcher


import datetime

class BasicMicroParsingPlugin(IPlugin):
    
    def __init__(self, parser=None):
        self.parser = parser
        
    def install(self, ctx):
        if not self.parser:
            self.parser = Parser(configure=ctx.di.configure)
        ctx.di['parser'] = self.parser

    def start_up(self, ctx):
        ctx.er.parser_filters.track(self.parser.add_micro_parser)
        ctx.er.parser_actions.track(self.parser.add_action)

        re_parser = CommandsParser()
        ctx.er.message_patterns.track(re_parser)
        
        ctx.er.parser_filters.add(re_parser)
        
        ctx.er.parser_filters.add(TagExtractor())
        ctx.er.parser_filters.add(TokenizerParser())
        ctx.er.parser_filters.add(OutputSelector())

class TokenizerParser(IMicroParser):

    """Consumes: incoming_message"""
    """Produces: tokens, first_word"""

    def __init__(self):
        self.is_preceeded_by = ['head', 'incoming_message']
        self.is_followed_by = ['tokens', 'first_word']

    def micro_parse(self, metadata):
        tokens = map(lambda s: s.lower().strip(), metadata['incoming_message'].split())
        metadata['tokens'] = tokens
        if len(tokens):
            metadata['first_word'] = tokens[0]
        else:
            metadata['STOP'] = True
            metadata['first_word'] = ""

class CommandsParser(IMicroParser):
    
    def __init__(self, re_dispatch=REDispatcher()):
        self.is_preceeded_by = ['incoming_message', 'user_id']
        self.is_followed_by = ['command']

        self.dispatch = re_dispatch
        
    def register(self, pattern, fn):
        """Add a regular expression pattern and a function to run if the message matches the pattern. 
        Matching groups will be available from the dictionary passed to the function."""
        if hasattr(pattern, 'match'):
            self.dispatch.register_re(pattern, fn)
        else:
            self.dispatch.register_pattern(pattern.__str__(), fn)
    
    def micro_parse(self, metadata):
        string = metadata['incoming_message']
        self.dispatch.search(string, metadata)

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


class OutputSelector(IMicroParser):
    
    def __init__(self):
        self.is_preceeded_by = ['command', 'is_reminder', 'event_datetime', 'tags', 'special_tags']
        self.is_followed_by = ['execute_command', 'output_medium']
       
    def micro_parse(self, metadata):
        # TODO make sure that this is correct as per the User preferences.
        metadata.setdefault('reminder_medium', metadata['input_medium'])
        
        tags = filter(lambda x : x in ('noconfirm', 'noreminder'), metadata['tags'])
        metadata['tags'] = filter(lambda x : x in tags, metadata['tags'])
        metadata['special_tags'].extend(tags)
        
        
        metadata['output_medium'] = ""
        
        # check we actually have some input.
        if len(metadata.get('incoming_message', "")) == 0:
            return
        elif not metadata.get('command', None):
                metadata['command'] = 'unknown_command'
                metadata['execute_command'] = True
                metadata['output_medium'] = metadata['reply_medium']
                return
        
        if metadata.get('is_reminder', None):
            # if this is a reminder, 
            if 'noreminder' not in tags:
                metadata['execute_command'] = True
                metadata['output_medium'] = metadata['reminder_medium']
        else:
            # this is a reply, and we probably need to talk back.
            metadata['output_medium'] = metadata.get('reply_medium', metadata['input_medium'])
            if metadata.has_key('event_datetime'):
                # a reply to a schedule request.
                if 'noconfirm' not in tags:
                    tz = datetime.timedelta(seconds=metadata.get('tz_offset', 0))
                    schedule_time_tz = metadata['event_datetime'] + tz
                    metadata['execute_command'] = False
                    metadata['schedule_time_tz'] = schedule_time_tz
            else:
                metadata['execute_command'] = True
                