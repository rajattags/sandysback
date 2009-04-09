from sandy2.common.parsing import IMicroParser, IMessageAction, Parser
from sandy2.common.plugins import IPlugin

class ConsolePlugin(IPlugin):
    
    def __init__(self, parser=None):
        self.parser=parser
        self._is_running = True
        pass
    
    def start_up(self):
        self._is_running = True
        self.parser.add_micro_parser(ConsoleUserFinder())
        self.parser.add_micro_parser(ConsoleOutputSetter())
        self.parser.add_micro_parser(ExitCommand())
        
        self.parser.add_action(ConsoleOutputReply())
    
    def run(self):
        print "Sandy console. Try 'help' to inspect what words I understand available."
        input = None
        while (self._is_running):
            input = raw_input('>> ')
            self.do_command(input)

    def do_command(self, message):
        metadata = self.parser.parse({"incoming_message": message, "input_medium": "stdin", "tz_offset" : 0})
        self.parser.perform_actions(metadata)
        return metadata


    def stop(self):
        self._is_running = False

class ExitCommand(IMicroParser):
    def __init__(self):
        self.is_preceeded_by = ['input_medium', 'first_word']
        self.plugin_system = None

    def micro_parse(self, metadata):
        if metadata['input_medium'] == 'stdin' and metadata['first_word'] == 'exit' and self.plugin_system is not None:
            self.plugin_system.stop()
            print "Bye"
            metadata['STOP'] = True
        
            

class ConsoleUserFinder(IMicroParser):

    """Consumes: input_medium
    Produces: user
    """
    def __init__(self):
        self.is_preceeded_by = ['input_medium']
        self.is_followed_by = ['user_id']

    def micro_parse(self, metadata):
        if metadata.setdefault('input_medium', 'stdin') == 'stdin':
            import os
            username = os.getenv("USERNAME", "unknown user")
            metadata['fullname'] = username
            # not really necessary if we don't use the db.
            metadata['console_id'] = username
            metadata['user_id'] = -1

class ConsoleOutputSetter(IMicroParser):

    """Consumes: input_medium
    Produces: reply_medium
    """

    def __init__(self):
        #self.is_preceeded_by = ['input_medium']
        self.is_followed_by = ['reply_medium', 'reminder_medium']
        

    def micro_parse(self, metadata):
        if metadata.setdefault('input_medium', 'stdin') == 'stdin':
            metadata.setdefault('reply_medium', 'stdout')
            metadata.setdefault('reminder_medium', 'stdout')

class ConsoleOutputReply(IMessageAction):
    def perform_action(self, metadata):        
        medium = metadata['output_medium']
        if medium == 'stdout':
            message = metadata['output_message']
            print message
            

