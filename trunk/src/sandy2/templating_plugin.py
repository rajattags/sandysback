from sandy2.common.parsing import IMessageAction, IMicroParser
from sandy2.common.plugins import IPlugin

#from mako import exceptions



from sandy2.ui.template import dictionary_viewer
from sandy2.ui.template import PhraseBankParser, TemplateCollector

class TemplatingPlugin(IPlugin):
    
    def __init__(self):
        self.phrase_banks = PhraseBankParser()
        self.templates = TemplateCollector()
    
    def start_up(self, ctx):
        # parser has a read method that takes a single filename or list of filenames.
        ctx.er.phrase_banks.track(self.phrase_banks.register_file)
        ctx.er.template_files.track(self.templates.register_file)
        # we should tell the personalities to reset themselves.
        ctx.er.template_files.track(self.reset_base_templates)
        
        ctx.er.template_files.add(self, "ui/templates/utility.txt")
        ctx.er.phrase_banks.add(self, "ui/templates/zander_empty.txt")
        
        ctx.er.micro_parsers.add(PersonalitySetter())
        ctx.er.parser_actions.add(TemplatingAction(self.phrase_banks))

    def reset_base_templates(self, *args, **kw):
        self.phrase_banks.set_base_template(self.templates.get_template())

class PersonalitySetter(IMicroParser):
    def micro_parse(self, metadata):
        # read from the database.
        pass 
    
    
class TemplatingAction(IMessageAction):
    
    def __init__(self, phrase_banks, di=None):
        self._phrase_banks = phrase_banks
        self.is_preceeded_by = ['output_medium', 'is_reminder', 'event_datetime', 'tags', 'special_tags']
        self.is_followed_by = ['output_message']
        self.di = di
        pass
    
    def perform_action(self, metadata):
        agent_name = metadata.get('agent_name', 'zander')
        metadata.setdefault('command', 'no_command')
        try:
            phrase_bank = self._phrase_banks.get_phrasebank(agent_name)
            kw = {
                  'M'     : dictionary_viewer(metadata), 
                  'System': dictionary_viewer(self.di),
                  }
            
            template_name = 'payload' if metadata['execute_command'] else 'schedule_payload'
            metadata['output_message'] = phrase_bank.render(template_name, **kw)
            
        except Exception:
            print "_______________________________________"
            print phrase_bank._template.source
            print "_______________________________________"
            print exceptions.text_error_template().render()
        
      