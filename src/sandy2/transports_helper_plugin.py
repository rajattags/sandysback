from sandy2.common.parsing import IMicroParser, Parser
from sandy2.common.plugins import IPlugin


class TransportHelperPlugin(IPlugin):
    def __init__(self, parser=None, db=None, properties={}):
        self.is_preceeded_by = ['database', 'passwords']
        
        self.parser = parser
        self.database = db
        self.properties = properties
        self.mail_parser = None
        self.mail_sender = None
        self.mail_receiver = None
        self.dao_map = {}
        
    def install(self, ctx):
        ctx.er.transport_dao.track(self._register_dao)
        
    def start_up(self, ctx):
        ctx.er.parser_filters.add(TransportUserFinder('input_medium', self.dao_map))
        # one day, we may be able to switch between input and output medium.
        ctx.er.parser_filters.add(TransportUserFinder('output_medium', self.dao_map))
        ctx.er.parser_filters.add(TransportUserCreator(self.dao_map))
        
    def _register_dao(self, transport_id, dao):
        """Register a transport name and Data Access Object. e.g. 'email', EmailDAO()""" 
        self.properties.configure(dao)
        dao.create_tables()
        self.dao_map[transport_id] = dao
        
    def run(self):
        pass
        
    def stop(self):
        pass
        
class TransportUserFinder(IMicroParser):

    def __init__(self, medium='input_medium', dao_map=None):
        self.id = "TransportUserFinderFor_%s" % (medium)
        self.is_preceeded_by = ['tx', medium, 'incoming_message']
        self.is_followed_by = ['user_id'] if (medium is 'input_medium') else []
        self.dao_map=dao_map
        self.medium = medium

    def micro_parse(self, metadata):
        key = metadata[self.medium]
        if self.dao_map.has_key(key):
            results = self.dao_map[key].find_row(metadata)
            metadata.add_dictionary(results)

class TransportUserCreator(IMicroParser):
    def __init__(self, dao_map=None, parser=None):
        self.is_preceeded_by = ['tx', 'create_new_user']
        self.dao_map=dao_map
        self.parser = parser

    def micro_parse(self, metadata):
        if metadata.get('create_new_user', False):
            # we don't need to respond to anything from a stranger that we don't understand.
            key = metadata['input_medium']
            if self.dao_map.has_key(key):
                self.dao_map[key].save_row(metadata)

                # reparse, now we've inserted some stuff into the user table.
                self.parser.parse(metadata)