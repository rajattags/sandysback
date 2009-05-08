from sandy2.common.plugins import IPlugin

class PasswordPlugin(IPlugin):
    
    def __init__(self, di=None):
        self.is_followed_by = ['passwords']
        self.di = di
        pass
    
    def install(self):
        
        self.di['gmail_user'] = ''
        self.di['gmail_password'] = ''
        
        self.di['agent_name'] = 'Zander'        
        self.di['mysql_user'] = 'root'
        self.di['mysql_password'] = 'MySQL-root-0'
        self.di['mysql_db'] = 'zander_test_database'
        self.di['mysql_host'] = '127.0.0.1'
        self.di['mysql_port'] = 3306
        
    