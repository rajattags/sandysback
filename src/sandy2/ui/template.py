from ConfigParser import RawConfigParser

from mako.runtime import Context
from mako.template import Template

from StringIO import StringIO


def _absolute_file(*path_elements):
    import inspect
    from os.path import join as pathjoin, dirname
    path = []
    
    for p in path_elements:
        if isinstance(p, str):
            path.append(p)
        else:
            path.append(dirname(inspect.getmodule(p).__file__))
    
    return pathjoin(*path)
    
def context(buffer = None, **maps):
    if not buffer:
        buffer = StringIO()

    ctx = Context(buffer, **maps)
    return ctx

def dictionary_viewer(dict):
    class DV:
        def __getattr__(self, key):
            if hasattr(dict, key):
                return getattr(dict, key)
            elif hasattr(dict, '__getitem__'):
                return dict[key]
            else:
                raise KeyError(key)
        def __getitem_(self, key):
            return dict[key]
        def has_key(self, key):
            return dict.has_key(key)
        def get(self, key, default):
            return dict.get(key, default)
    return DV()

def render_template(template, **data):
    ctx = context(**data)
    buf = ctx._buffer_stack[0]

    try:
        template.render_context(ctx)
        out = buf.getvalue()
        return out
    except:
        from mako.exceptions import RichTraceback
        traceback = RichTraceback()
        for (filename, lineno, function, line) in traceback.traceback:
            print "File %s, line %s, in %s" % (filename, lineno, function)
            print line
        print "%s: %s" % (str(traceback.error.__class__.__name__), traceback.error)


class PhraseBank:
    
    def __init__(self, template=None):
        self._phrases = {}
        self._src = template.source if template else ""
        self._template = None
    
    def set_template(self, template):
        if template:
            self._src = template.source
        self._template = None
    
    def __setitem__(self, key, value):
        list = self._phrases.setdefault(key, [])
        list.append(value)
    
    def __getitem__(self, key):
        list = self._phrases[key]
        return list[-1]
    
    def render(self, defName=None, **data):
        if not self._template:
            src = "%s\n%s" % (self._src, self._generate_mako(self._phrases))
            self._template = Template(src, format_exceptions=False)
        
        if not defName:
            template = self._template
        elif self.has_key(defName):
            template = self._template.get_def(defName)
        else:
            raise ValueError()
        return render_template(template, TEMPLATE=template, **data)
    
    def has_key(self, key):
        if self._template and self._template.has_def(key):
            return True
        else:
            return self._phrases.has_key(key)
        
        
    def _generate_mako(self, phrase_dict):
        outer_funcs = []
        for phrase_name_and_args, phrase_texts in phrase_dict.items():
            
            # handle the case where no bracket has been added
            if '__name__' is phrase_name_and_args:
                continue
            if "(" in phrase_name_and_args:
                # slice the arglist of the function.
                open = phrase_name_and_args.index('(')
                phrase_name = phrase_name_and_args[:open]
                ending = phrase_name_and_args[open:]
            else:
                # add one by default
                ending = "()"
                phrase_name = phrase_name_and_args
            
            
            # generate an inner def for each value of the phrase we've got.
            inner_func_names = []
            inner_funcs = []
            index = 0
            for phrase in phrase_texts:
                inner_func_name = "_%s_%s" % (index, phrase_name)
                inner_funcs.append("<%%def name='%s%s'>%s</%%def>" % (inner_func_name, ending, phrase))
                inner_func_names.append(inner_func_name)
                index = index + 1
            
            outer_dict = { 'phrase_name': phrase_name, 
                          'arg_list': ending,
                          'inner_funcs': "".join(inner_funcs),
                          'inner_func_names': ", ".join(inner_func_names), 
                          }
            # then generate a custom python routine which will select a random def and call it.
            single_func = """
<%%def name='%(phrase_name)s%(arg_list)s'>%(inner_funcs)s<%%
    fns = [%(inner_func_names)s]
    import random
    random.sample(fns, 1)[0]%(arg_list)s
%%></%%def>""" % outer_dict
            
            outer_funcs.append(single_func)
            
        return "\n".join(outer_funcs)
    
    
class PhraseBankParser(RawConfigParser):
    
    def __init__(self, defaults={}):
        RawConfigParser.__init__(self, defaults)
        self._dict = PhraseBank
        self._template = None
    
    def add_section(self, section):
        if section not in self._sections:
            self._sections[section] = self._dict()
        
    def get_phrasebank(self, section):
        if not self._sections.has_key(section):
            raise KeyError(section)
        else:
            return self._sections[section]
        
    def register_file(self, *path_elements):
        self.read(_absolute_file(*path_elements))
        self.set_base_template(self._template)
        
    def set_base_template(self, template):
        if template:
            for key, pb in self._sections.items():
                pb.set_template(template)
        self._template = template



class TemplateCollector:
    
    def __init__(self):
        self._file_set = set()
        self._uber_template = None
        pass
    
    def register_file(self, *path_elements):
        filename = _absolute_file(*path_elements)
        self._file_set.add(filename)
        self._uber_template = None
    
    def get_template(self, def_name=None):
        if self._uber_template is None:
            buf = StringIO()
            for file in self._file_set:
                t = Template(filename=file)
                buf.write(t.source)
            
            self._uber_template = Template(buf.getvalue(), module_directory='/tmp/mako')
            buf.close()
        
        if self._uber_template.has_def(def_name):
            return self._uber_template.get_def(def_name)
        else:
            return self._uber_template
        