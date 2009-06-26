from sandy2.common.parsing import IMicroParser, IMessageAction, Parser
from sandy2.common.plugins import IPlugin

class ConsolePlugin(IPlugin):
    
    def __init__(self, parser=None):
        self.parser=parser
        self.__listener = ConsoleListener(self.do_command)
        pass
    
    def start_up(self, ctx):
        self._is_running = True
        ctx.er.parser_filters.add(ConsoleUserFinder())
        ctx.er.parser_filters.add(ConsoleOutputSetter())
        ctx.er.message_patterns.add('^(exit|quit)', ExitCommand().exit)
        
        ctx.er.parser_actions.add(ConsoleOutputReply())
              
    
    def run(self):
        if self.__listener:
            self.__listener.start()

    def do_command(self, message):
        metadata = self.parser.parse({"incoming_message": message, "input_medium": "stdin", "tz_offset" : 0})
        self.parser.perform_actions(metadata)
        return metadata


    def stop(self):
        if self.__listener:
            self.__listener._is_running = False

import threading
class ConsoleListener(threading.Thread):
    
    def __init__(self, fn):
        threading.Thread.__init__(self)
        self._is_running = False
        self.do_command = fn
    
    def run(self):
        self._is_running = True
        print "Sandy console. Try 'help' to inspect what words I understand available."
        input = None
        while (self._is_running):
            input = raw_input('>> ')
            self.do_command(input)

class ExitCommand:

    def __init__(self, plugin_framework=None):
        self.plugin_framework = plugin_framework

    def exit(self, metadata):
        if metadata['input_medium'] == 'stdin'  and self.plugin_framework is not None:
            self.plugin_framework.stop()
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
    def __init__(self):
        self.is_preceeded_by = ['output_medium', 'output_message']
    
    def perform_action(self, metadata):        
        medium = metadata['output_medium']
        if medium == 'stdout':
            message = metadata['output_message']
            print message
            