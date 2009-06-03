
from sandy2.transports.mailer import MailParser, MailSender, MailListener

class SimpleResponder:
    def __init__(self):
        pass
    def run(self):
        parser = MailParser(email_address=['zander.dev@gmail.com', 'zander.dev@googlemail.com'], fullname='Zander The Wonderhorse')
        sender = MailSender(username='zander.dev@googlemail.com', password='PASSWORD_THAT_ISNT_THIS')
        receiver = MailListener(username='zander.dev@googlemail.com', password='PASSWORD_THAT_ISNT_THIS')
        
        
        for txt in receiver.run():
            message = parser.parse_raw_mail(txt)
            metadata = parser.find_metadata(message)
            metadata['reminder_message'] = "It's time to get up"
            reply = parser.construct_email(metadata, 'reminder_message')
            
            sender.send(reply)
        sender.disconnect()
        
        
if __name__ == '__main__':
    SimpleResponder().run()