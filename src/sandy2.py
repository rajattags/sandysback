from sandy2.common.plugins import PluginSystem

from sandy2.base_plugin import BasicMicroParsingPlugin
from sandy2.console_plugin import ConsolePlugin
from sandy2.database_plugin import DatabasePlugin
from sandy2.introspection_plugin import IntrospectionPlugin
from sandy2.gmail_plugin import GmailPlugin
from sandy2.message_db_plugin import MessageDBPlugin
from sandy2.reminder_plugin import SchedulerPlugin
from sandy2.reminder_db_plugin import SchedulerDBPlugin


class Sandy2(object):

    def __init__(self):
        pass



        
    def run(self):
        plugins = [ 
                   DatabasePlugin(),
                   MessageDBPlugin(),
                   SchedulerPlugin(),
                   ConsolePlugin(),
                   BasicMicroParsingPlugin(),
                   IntrospectionPlugin(),
                   SchedulerDBPlugin(),
                   GmailPlugin(),
                ]
        
        PluginSystem(plugins).start()



if __name__ == "__main__":
    Sandy2().run()