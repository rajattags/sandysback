from sandy2.ordering import topological_sort, INode

""" The main parsing module. This really is just a scaffold around micro-parsers
and actions supplied externally.
"""


class Parser(object):
    """Variable: micro_parsers

    An ordered list of micro-parsers. These will be sorted according to their
    dependencies.
    """
    micro_parsers = []

    """Variable: micro_parsers

    The list of actions that are to be run after all micro-parsers have been
    run.
    """
    actions = []

    _ordered = False

    def __init__(self, micro_parsers=[], actions=[]):
        self.actions = actions
        self.micro_parsers = micro_parsers
        self._ordered = False

    def parse_message(self, message):
        return self.parse({"incoming_message": message, "incoming_medium": "stdin"})

    def parse(self, metadata):
        """Parse the message contained in the metadata.

        Metadata can include data other than the message, which may be
        considered by microparsers.

        No restriction is made upon exactly what processing is done in the
        micro-parsers: for example this may be simple pattern matching,
        parts-of-speech tagging, or a context free grammar parser.
        """
        if not self._ordered:
            # we only need to do the sort when we've added more micro-parsers.
            self.micro_parsers = topological_sort(self.micro_parsers)
            self._ordered = True

        for t in self.micro_parsers:
            if self._can_continue(metadata):
                # todo: check that this method actually exists.
                t.micro_parse(self, metadata)
            else:
                break

        return metadata

    def _can_continue(self, metadata):
        """The STOP key should be used to prematurely terminate processing of a 
        command. 
        
        This would probably be useful for micro-parsers or commands that call 
        the parser recursively.
        """
        return metadata.get('STOP', None) is None

    def perform_actions(self, metadata):
        """Perform the actions in the order they were registered.
        """
        for a in self.actions:
            if self._can_continue(metadata):
                # todo: check that this method actually exists.
                a.perform_action(self, metadata)
            else:
                break

    def add_micro_parser(self, new_parser):
        self.micro_parsers.append(new_parser)
        self.ordered = False

    def add_action(self, new_action):
        self.actions.append(new_action)


class IMicroParser(INode):

    """An interface to let plugins help with parsing"""

    def micro_parse(self, parser, metadata):
        """The single method can add or remove entries to the metadata dictionary.

        MicroParsers may cooperate with one another, or with other actions.
        """


class IMessageAction(INode):

    """An interface to let plugins add extra actions to the parser."""

    def perform_action(self, parser, metadata):
        """This single method should perform any action that should occur after all parsing has completed."""