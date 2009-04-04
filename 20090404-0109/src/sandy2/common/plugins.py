from sandy2.common.di import Injector
from sandy2.common.ordering import DependencyList
from sandy2.common.parsing import Parser


class IPlugin:
    """Interface class for documenting the plugin methods called by the plugin system.
    """
    
    def __init__(self):
        pass

    def install(self):
        """Method to be run before any start-up methods are run. Any initial first time code should be run here, 
        though the detection of whether this is the first time this plugin is used is left up to the plugin.
        """
        pass
    
    def start_up(self):
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
 
 
class PluginSystem:
    """Container for configuring and starting a set of plugins.
    Internally the plugins are ordered with a dependency graph. A plugin may use:
        self.is_preceeded_by = ['database'] # requires the database 
        self.is_followed_by = ['user_table'] # provides a user_table
        
    to what it imports and exports or what it depends upon, or must come before. 
    """
    def __init__(self, plugins=[], di=Injector()):
        self.plugins = DependencyList(plugins)
        self.di = di
    
        di['properties'] = di
        di['configure'] = di.configure
        # this should be split into its own plugin.
        di['parser'] = Parser(configure=di.configure)

    
    def configure(self):
        """Configure, install and start all plugins. Currently this is called by calling self.run(), 
        so only useful outside of the context of the run method. e.g. testing
        """
        for p in self.plugins:
            self.di.configure(p)
            p.install()
        
        for p in self.plugins:
            p.start_up()


    def start(self):
        """Configure and run all plugins passed to the constructor.
        """
        self.configure()
        
        for p in self.plugins:
            p.run()    
   