from sandy2.common.di import Injector
from sandy2.common.ordering import DependencyList
from sandy2.common.extensions import ExtensionRegistry

class IPlugin:
    """Interface class for documenting the plugin methods called by the plugin system.
    """
    
    def __init__(self):
        pass

    def install(self, ctx):
        """Method to be run before any start-up methods are run. Any initial first time code should be run here, 
        though the detection of whether this is the first time this plugin is used is left up to the plugin.
        """
        pass
    
    def start_up(self, ctx):
        """Method to be run just prior the main event loops are launched. This is guaranteed to be run after everything has been installed.
        """
        pass
    
    def run(self):
        """Start an event loop in this method.
        This is the opportunity to spawn any long running threads in this method.
        """
        pass    
    
    def stop(self):
        """Currently unused, but a placeholder for any shutdown or dispose code that needs to be executed just prior to the plugin stopping.
        """
        pass
    
    def uninstall(self):
        """Another placeholder, for any uninstall logic the plugin may want to employ to clean up after itself.
        """
        pass
 
 
class PluginFramework:
    """Container for configuring and starting a set of plugins.
    Internally the plugins are ordered with a dependency graph. A plugin may use:
        self.is_preceeded_by = ['database'] # requires the database 
        self.is_followed_by = ['user_table'] # provides a user_table
        
    to what it imports and exports or what it depends upon, or must come before. 
    """
    def __init__(self, plugins=[], di=Injector()):
        self.plugins = DependencyList(plugins)
        self.di = di
    
        self.extension_registry = ExtensionRegistry(configure=self.di.configure)
    
        di['plugin_framework'] = self
        di['properties'] = di
        di['di'] = di
        di['configure'] = di.configure
        

        
    
    def configure(self):
        """Configure, install and start all plugins. Currently this is called by calling self.run(), 
        so only useful outside of the context of the run method. e.g. testing
        """
        ctx = PluginContext(self.di, self.extension_registry)
        self._call_on_all_plugins('install', self.di.configure, ctx)
        self._call_on_all_plugins('start_up', None, ctx)

    def _call_on_all_plugins(self, fn_name, pre_call_function, *args, **kw):
        for p in self.plugins:
            if hasattr(p, fn_name) and callable(getattr(p, fn_name)):
                
                try:
                    #print "PLUGIN %s: %s" % (fn_name, str(p))
                    if pre_call_function is not None:
                        pre_call_function(p)
                    getattr(p, fn_name)(*args, **kw)
                except:
                    import sys, traceback
                    traceback.print_exc()
                    continue

    def start(self):
        """Configure and run all plugins passed to the constructor.
        """
        self.configure()
        self._call_on_all_plugins('run', None)  
   
    def stop(self):
        self._call_on_all_plugins('stop', None)
        

class PluginContext:
    
    def __init__(self, dependency_injector=Injector(), extension_registry=ExtensionRegistry()):
        self.er = extension_registry
        self.di = dependency_injector