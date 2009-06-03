import unittest

from sandy2.ui.template import context, dictionary_viewer, render_template
from sandy2.ui.template import PhraseBank, PhraseBankParser, TemplateCollector

from mako.template import Template

class PhraseBankTest(unittest.TestCase):
    
    def setUp(self):
        self.pb = PhraseBank()
        pass
    
    def testGenerateSingleValuePhrase(self):
        fn_name = 'char'
        
        # first generate a function with only one value
        src = self.pb._generate_mako({fn_name: ['a']})
        print src
        
        t = Template(src).get_def(fn_name)
        out = "".join(map(lambda n:t.render(), range(0,10)))
        
        self.assertEquals("aaaaaaaaaa", out)
        
    def testGenerateMultiValuePhrase(self):
        # now generate a function with multiple possible values.
        fn_name = 'char'
        fn_values = ['a', 'b', 'c', 'd', 'e', 'f', 'g']
        src = self.pb._generate_mako({fn_name: fn_values})
        print src
        
        t = Template(src).get_def(fn_name)
        
        out = map(lambda n:t.render(), range(0,100))
        
        print "".join(out)
        
        for c in fn_values:
            self.assertTrue(c in out)
            
    def testGeneratePhraseWithArgs(self):
        fn_name = 'char'
        
        # first generate a function with only one value
        src = self.pb._generate_mako({fn_name + "(arg)": ['a']})
        print src
        
        t = Template(src).get_def(fn_name)
        out = "".join(map(lambda n:t.render(n), range(0,10)))
        
        self.assertEquals("aaaaaaaaaa", out)
        
        

        
    def testDict(self):
        
        fn = 'char'
        
        self.assertFalse(self.pb.has_key(fn))
        self.pb[fn] = 'a'
        
        self.assertTrue(self.pb.has_key(fn))
            
class PhraseBankParserTest(unittest.TestCase):
    
    def testParser(self):
        print """Testing the loading of new phrases via the config parser"""
        fn_values = ['a', 'b', 'c', 'd', 'e', 'f', 'g']
        agent = 'Alice'
        k = 'chars'

        p = PhraseBankParser()
        
        p.add_section(agent)
        for v in fn_values:
            p.set(agent, k, v)

        phrase_book = p.get_phrasebank(agent)

        out = map(lambda n:phrase_book.render(defName=k), range(0,100))
        out = "".join(out)
        
        
        print "out is", out
        for c in fn_values:
            if c not in out:
                print "%s not in out" % (c)
            self.assertTrue(c in out)
            
class TemplateRendererTest(unittest.TestCase):
    
    def setUp(self):
        self.renderer = TemplateCollector()
        self.renderer.register_file(self, "template.txt")
    
    def testRendering(self):
        print "+++++++++++++++++++++++++++++++++++++"
        print "testRendering()"
        
        template = self.renderer.get_template("loaded")

        try:
            txt = render_template(template, M=dictionary_viewer({'success':'correctly'}))
            print txt
            self.assertNotEquals(txt, None)
            self.assertEquals(txt, "Loaded correctly!")
        finally:
            print template.source
    

        
if __name__ == '__main__':
    unittest.main()


