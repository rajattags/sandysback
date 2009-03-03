import email
import email.utils
from email.message import Message
from email.MIMEText import MIMEText

from datetime import datetime, timedelta

from string import join

if __name__ == "__main__":
    pass

class MailParser(object):
    
    def __init__(self, email_address=None, fullname=None):
        self.prefix = "email_"
        if type(email_address) is str:
            email_address=[email_address]
        self.my_email_address = email_address
        
        self.my_email_name = fullname
        pass
    
    def parse_raw_mail(self, data):
        
        message = email.message_from_string(data)
        if not message.is_multipart():
            return message
        
        # we don't yet deal with multi part
        # or html messages
        
        return message
        
    def find_metadata(self, message, metadata={}):
        
        metadata[self.prefix + "my_address"] = self.my_email_address
        
#          o the transport specific username, and nickname of the sender
        from_ = message.get_all('from', [])
        all_from = email.utils.getaddresses(from_)
        metadata['email_user'] = all_from[0]
        metadata['email_id'] = all_from[0][1]
        metadata['fullname'] = all_from[0][0]
        
#          o additional receipients of the message.
        tos = message.get_all('to', [])
        ccs = message.get_all('cc', [])
        all_recipients = filter(lambda a : a[0] not in self.my_email_name and a[1] not in self.my_email_address, email.utils.getaddresses(tos + ccs))
        metadata['email_recipients'] = all_recipients

#          o the location where to respond

#          o the transport specific message id (if available)
        metadata['email_message_id'] = message['Message-ID']
        metadata['email_in_reply_to'] = message.get('In-Reply-To', None)
        
#          o the text as the user typed it
        subject = message['Subject']
        metadata['email_subject'] = subject
        payload = message.get_payload(decode=True)
        if type(payload) is str:
            metadata['incoming_message'] = "\n".join([subject, payload])
        else:
            for payload in message.get_payload():
                ct = payload['Content-Type']
                if ct.startswith('text/plain'):
                    metadata['incoming_message'] = "\n".join([subject, str(payload._payload)])


#          o the date sent, including timezone
        date_tuple = email.utils.parsedate_tz(message['Date'])
        tz_offset = date_tuple[9]
        datetime_local = datetime(*date_tuple[0:6])

        metadata['message_datetime_local'] = datetime_local
        metadata['tz_offset'] = tz_offset

#          o the transport name.
        metadata['input_medium'] = 'email'

        return metadata

    def construct_email(self, metadata, key='reminder_message'):
        message = MIMEText(metadata[key])
        message['To'] = email.utils.formataddr(metadata['email_user'])
        message['CC'] = ", ".join(map(lambda p: email.utils.formataddr(p), metadata['email_recipients']))
        
        message_id = metadata.get('email_message_id', None)
        if message_id:
            message['In-Reply-To'] = message_id
        
        message.set_payload(metadata.get(key, "Error message from %s" % (self.my_email_address)))
                            
        message['From'] = email.utils.formataddr((self.my_email_name, self.my_email_address[0]))
        message['Subject'] = "Re: " + metadata['email_subject']
        
        return message
    
    def run(self):
        pass



import smtplib

class MailSender:
    
    def __init__(self, mailhost='smtp.gmail.com', port=587, username=None, password=None):
        self.mailhost = mailhost
        self.username = username
        self.password = password
        self.port = port
        
        self.server = None
        self.connected = False
        
    def connect(self):
        self.server = smtplib.SMTP(self.mailhost, self.port)
        self.server.set_debuglevel(1)
        # Start the conversation with EHLO
        self.server.ehlo()

        # Gmail uses TLS.
        self.server.starttls()

        self.server.ehlo()

        # Login to the server with SMTP AUTH now that we're TLS'd and client identified
        self.server.login(self.username, self.password)
        self.connected = True
    
    def send(self, mime):
        if not self.connected:
            self.connect()
        try:
            failed = self.server.sendmail(mime['From'], [mime['To'], mime['CC']], mime.as_string())
            print failed
            self.server.noop()
        except Exception:
            self.connected = False
            send(mime)
        finally:
            pass

    
    def disconnect(self):
        try:
            self.server.rset()
            self.server.close()
        except:
            pass
        finally:
            self.connected = False
        
class MailListener(object):


    def __init__(self, mailhost='imap.gmail.com', port=993, username=None, password=None):
        self.mailhost = mailhost
        self.port = port
        self.username = username
        self.password = password
        pass
    
    def run(self):
        from threading import Thread
        import imaplib
        import time

        M = imaplib.IMAP4_SSL(self.mailhost, self.port)
        M.login(self.username, self.password)
        while True:
            M.select()
            typ, data = M.search(None, '(UNSEEN)')
            for num in data[0].split():
                typ, d = M.fetch(num, '(RFC822)')
                M.store(num, "+FLAGS", '\\Seen')
                yield d[0][1]
            time.sleep(120)
            
        M.close()
        M.logout()

        