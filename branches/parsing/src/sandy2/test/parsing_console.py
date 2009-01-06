from sandy2.parsing import IMicroParser, IMessageAction, Parser
from string import join
from time import ctime


class Console(object):

    parser = None

    def __init__(self):
        self.parser = Parser()

        self.parser.add_micro_parser(ConsoleUserFinder())
        self.parser.add_micro_parser(ConsoleOutputSetter())
        self.parser.add_micro_parser(HelpCommand())
        self.parser.add_micro_parser(InspectCommand())
        self.parser.add_micro_parser(TokenizerParser())
        self.parser.add_micro_parser(LogCommand())
        self.parser.add_micro_parser(TagExtractor())

        self.parser.add_action(ConsoleOutputReply())


    def run(self):
        print "Sandy console. Try 'inspect' to inspect what micro-parsers are available."
        input = None
        while (input is not 'exit'):
            input = raw_input('>> ')
            self.do_command(input)



    def do_command(self, message):
        metadata = self.parser.parse_message(message)
        metadata['debug'] = True
        self.parser.perform_actions(metadata)
        return metadata

class ConsoleUserFinder(IMicroParser):

    """Consumes: input_medium"""
    """Produces: user"""
    def __init__(self):
        self.id = self.__class__.__name__
        self.is_followed_by = ['abstract_user_finding']

    def micro_parse(self, parser, metadata):
        if metadata.setdefault('input_medium', 'stdin') == 'stdin':
            metadata['user'] = 'dude'

class ConsoleOutputSetter(IMicroParser):

    """Consumes: input_medium"""
    """Produces: reply_medium"""

    def __init__(self):
        self.id = self.__class__.__name__
        self.is_followed_by = ['abstract_output_format']

    def micro_parse(self, parser, metadata):
        if metadata.setdefault('input_medium', 'stdin') == 'stdin':
            metadata.setdefault('reply_medium', 'stdout')

class InspectCommand(IMicroParser):
    """Consumes: tokens"""
    """Produces: reply_message"""

    """Short description: Display all micro-parsers in order"""
    def __init__(self):
        self.is_preceeded_by = ['tokens']

    def micro_parse(self, parser, metadata):
        first_word = metadata['tokens'][0]
        if len(metadata['tokens']) > 1:
            second_word = metadata['tokens'][1]
        else:
            second_word = 'all'

        if first_word in ['inspect']:
            if (second_word in ['parsers', 'all']):
                replies = map(lambda s: s.id, parser.micro_parsers)
            metadata['reply_message'] = "Parsers:\n\t-> " +join(replies, " \n\t-> ")

class HelpCommand(IMicroParser):

    """Consumes: tokens, user"""
    """Produces: reply_message"""

    """Short description: illustrative, but useless command"""
    """Long description : """

    def __init__(self):
        self.is_preceeded_by = ['abstract_user_finding', 'tokens']

    def micro_parse(self, parser, metadata):
        first_word = metadata['tokens'][0]
        if first_word in ['help', 'h', '?']:
            metadata['reply_message'] = join(["Zoinks, ", metadata['user'], "! It's the ghost"], '')

class LogCommand(IMicroParser):

    """Consumes: tokens"""

    def __init__(self):
        self.is_preceeded_by = ['abstract_user_finding', 'tokens']

    def micro_parse(self, parser, metadata):
        first_word = metadata['tokens'][0]
        if first_word in ['log', 'l']:
            metadata['reply_message'] = join([ctime(), ' ', metadata['user'], ': ', metadata['incoming_message']], '')


class TokenizerParser(IMicroParser):

    """Consumes: incoming_message"""
    """Produces: tokens"""

    def __init__(self):
        self.id = 'tokens'

    def micro_parse(self, parse, metadata):
        metadata['tokens'] = map(lambda s: s.strip().lower(), metadata['incoming_message'].split(' '))

class TagExtractor(IMicroParser):
    """Consumes: tokens"""
    """Produces: tags"""

    def __init__(self):
        self.id = 'tags'
        self.is_preceeded_by = ['tokens']

    def micro_parse(self, parser, metadata):
        tags = filter(lambda s: s.startswith('#'), metadata['tokens'])
        metadata['tags'] = tags

class ConsoleOutputReply(IMessageAction):
    def perform_action(self, parser, metadata):
        message = metadata.get('reply_message', "Sorry, I don't understand what you typed")
        if metadata['reply_medium'] == 'stdout':
            print join(['REPLY: ', message], '')
            if metadata.get('debug', False):
                print metadata



if __name__ == "__main__":
    Console().run()