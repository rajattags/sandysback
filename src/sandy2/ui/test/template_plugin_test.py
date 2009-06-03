import unittest

from sandy2.common.plugins import PluginContext

from mako import exceptions

class TemplatePluginTest(unittest.TestCase):
    
    def testIntegration(self):
        from sandy2.templating_plugin import TemplatingPlugin
        self.plugin = TemplatingPlugin()
        ctx = PluginContext()
        self.plugin.start_up(ctx)
        
        ctx.er.template_files.add(self, "templates/test_format.txt")
        ctx.er.phrase_banks.add(self, "templates/phrasebanks.txt")
        
        # not the recommended way of getting the phrasebanks.
        phrase_banks = self.plugin.phrase_banks
        

        try:
            template = phrase_banks.get_phrasebank('nobody')
            print template.render()
            
            template = phrase_banks.get_phrasebank('somebody')
            print template.render()
        except:
            print "_______________________________________"
            print template._template.source
            print "_______________________________________"
            print exceptions.text_error_template().render()
        
        
            
        
if __name__ == '__main__':
    unittest.main()