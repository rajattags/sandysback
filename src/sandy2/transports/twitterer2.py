
import sys

from datetime import datetime, timedelta
from email.message import Message
from email.MIMEText import MIMEText
from string import join

from twitter import Twitter



if __name__ == "__main__":
    pass

class MailParser(object):
    
    def __init__(self, email_address=None, fullname=None):
        self.prefix = "email_"
        if type(email_address) is str:
            email_address=[email_address, email_address.replace("gmail.com", "googlemail.com")]
        self.my_email_address = email_address
        if fullname is None:
            fullname = []
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
        
        all_recipients = [a[0] for a in email.utils.getaddresses(tos + ccs) if (a[0] not in self.my_email_name and a[1] not in self.my_email_address)]
#        all_recipients = filter(lambda a : a[0] not in self.my_email_name and a[1] not in self.my_email_address, email.utils.getaddresses(tos + ccs))
        metadata[self.prefix + 'recipients'] = all_recipients

#          o the location where to respond

#          o the transport specific message id (if available)
        metadata[self.prefix + 'message_id'] = message['Message-ID']
        metadata[self.prefix + 'in_reply_to'] = message.get('In-Reply-To', None)
        
#          o the text as the user typed it
        subject = message['Subject']
                
        # check if the command exists on the subject.
        if subject:
            s = subject.lower()
            if s.startswith("re:") or s.startswith("[") or s.startswith("fw:") or s.startswith("fwd:"):
                subject = ""
        else:
            s = ""
            subject = ""
        metadata[self.prefix + 'subject'] = subject

        subject = subject + "\n\n"
        
        payload = message.get_payload(decode=True)
        if type(payload) is str:
            cleaned_message = "\n".join([subject, payload])
        else:
            for payload in message.get_payload():
                ct = payload['Content-Type']
                if ct.startswith('text/plain'):
                    cleaned_message = "\n".join([subject, str(payload._payload)])

        cleaned_message = "\n".join(filter(lambda line: not line.strip().startswith(">"), cleaned_message.splitlines())).strip()

        (left, sep, right) = cleaned_message.partition("\n\n")

        metadata['incoming_message'] = left

        metadata[self.prefix + 'body'] = cleaned_message

#          o the date sent, including timezone
        date_tuple = email.utils.parsedate_tz(message['Date'])
        tz_offset = date_tuple[9]
        if not tz_offset:
            tz_offset = 0

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
        
        print message
#        evt_date = metadata['']
#        message['Date'] = evt_date
        # TODO add Date header.
        return message
    
    def run(self):
        pass



import smtplib

class TwitterSender:
    
    def __init__(self, twitter):
        self.twitter = twitter
                
    def send(self, metadata):
        try:
            twitter_id = metadata['twitter_id']
            self.twitter.direct_messages.new(user=twitter_id, text=metadata[''])
        except:
            e = sys.exc_info()[0]
            print "Error found while sending mail: ", e
            self.connected = False
            self.send(mime)
        finally:
            pass

from threading import Thread
class TwitterListener(Thread):

    def __init__(self, twitter, delay=120, listener=None):
        Thread.__init__(self)
        self.twitter = twitter
        self.delay = delay
        self.__listener = listener
        self.__running = True

    
    def run(self):
        import time

        while self.__running:
            try:
#                M = imaplib.IMAP4_SSL(self.mailhost, self.port)
#                M.login(self.username, self.password)
#                M.select()
#                typ, data = M.search(None, '(UNSEEN)')
#                
#                nums = data[0].split()
#                if len(nums):
#                    print "Found %s new emails at %s" % (len(nums), self.username) 
#                
#                for num in nums:
#                    typ, d = M.fetch(num, '(RFC822)')
#                    M.store(num, "+FLAGS", '\\Seen')
#                    
#                    self.__listener(d[0][1])
#                M.close()
#                M.logout()
                pass
            except:
                import traceback
                traceback.print_exc()
                e = sys.exc_info()[0]
                print "Error found in listening for mail: ", e

            t = 0
            while t < self.delay and self.__running:
                time.sleep(5)
                t = t + 5
        


    def close(self):
        self.__running = False