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
            email_address=[email_address, email_address.replace("gmail.com", "googlemail.com")]
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
        
    def find_metadata(self, message, metadata=None):
        if not metadata:
            metadata = {}
        metadata[self.prefix + "my_address"] = self.my_email_address
        
#          o the transport specific username, and nickname of the sender
        from_ = message.get_all('from', [])
        all_from = email.utils.getaddresses(from_)
        userpair = all_from[0]
        metadata[self.prefix + 'id'] = userpair[1]
        metadata['fullname'] = userpair[0]
        
#          o additional receipients of the message.
        tos = message.get_all('to', [])
        ccs = message.get_all('cc', [])
        all_recipients = filter(lambda a : a[0] not in self.my_email_name and a[1] not in self.my_email_address, email.utils.getaddresses(tos + ccs))
        metadata[self.prefix + 'recipients'] = all_recipients

#          o the location where to respond

#          o the transport specific message id (if available)
        metadata[self.prefix + 'message_id'] = message['Message-ID']
        metadata[self.prefix + 'in_reply_to'] = message.get('In-Reply-To', None)
        
#          o the text as the user typed it
        subject = message['Subject']
        metadata[self.prefix + 'subject'] = subject
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
        if not tz_offset:
            tz_offset = 0
        if tz_offset > 12 or tz_offset < -12:
            tz_offset /= 3600
        datetime_local = datetime(*date_tuple[0:6])

        metadata['message_datetime_local'] = datetime_local
        metadata['tz_offset'] = tz_offset

#          o the transport name.
        metadata['input_medium'] = 'email'

        return metadata

    def construct_email(self, metadata, key='reminder_message'):
        message = MIMEText(metadata[key])
        message['To'] = email.utils.formataddr((metadata['fullname'], metadata[self.prefix + 'id']))
        # not sure if this line is very relevant atm.
        #message['CC'] = ", ".join(map(lambda p: email.utils.formataddr(p), metadata.get(self.prefix + 'recipients', ()))
        
        message_id = metadata.get(self.prefix + 'message_id', None)
        if message_id:
            message['In-Reply-To'] = message_id
        
        message.set_payload(metadata.get(key, "Error message from %s" % (self.my_email_address)))
                            
        message['From'] = email.utils.formataddr((self.my_email_name, self.my_email_address[0]))
        prefix = 'REMINDER: ' if metadata.get('is_reminder', False) else 'Re: '
        message['Subject'] = prefix + metadata[self.prefix + 'subject']
        # TODO add Date header.
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
        print "Connecting to SMTP..."
        self.server.set_debuglevel(0)
        # Start the conversation with EHLO
        self.server.ehlo()

        # Gmail uses TLS.
        self.server.starttls()

        self.server.ehlo()

        # Login to the server with SMTP AUTH now that we're TLS'd and client identified
        self.server.login(self.username, self.password)
        print "Connected to SMTP"
        self.connected = True
    
    def send(self, mime):
        if not self.connected:
            self.connect()
        try:
            print "Sending email"
            failed = self.server.sendmail(mime['From'], [mime['To'], mime['CC']], mime.as_string())
            print failed
            self.server.noop()
        except Exception:
            self.connected = False
            self.send(mime)
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


    def __init__(self, mailhost='imap.gmail.com', port=993, username=None, password=None, delay=120):
        self.mailhost = mailhost
        self.port = port
        self.username = username
        self.password = password
        self.delay = delay
        self.__running = True
    
    def run(self):
        from threading import Thread
        import imaplib
        import time

        while self.__running:
            M = imaplib.IMAP4_SSL(self.mailhost, self.port)
            M.login(self.username, self.password)
            M.select()
            typ, data = M.search(None, '(UNSEEN)')
            
            nums = data[0].split()
            if len(nums):
                print "Found %s new emails" % (len(nums)) 
            for num in nums:
                typ, d = M.fetch(num, '(RFC822)')
                M.store(num, "+FLAGS", '\\Seen')
                yield d[0][1]
            M.close()
            M.logout()
            if self.__running:
                time.sleep(120)
            

    def close(self):
        self.__running = False