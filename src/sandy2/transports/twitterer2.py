
import sys

from datetime import datetime, timedelta
from string import join

from twitter import Twitter

from threading import Thread
class TwitterService(Thread):
        
    def __init__(self, twitter, delay=120, listener=None, max_length=140):
        Thread.__init__(self)
        self.twitter = twitter
        self.delay = delay
        self.__listener = listener
        self.__running = True
        self.max_length = max_length
                
    def send(self, metadata):
        twitter_id = metadata['twitter_id']
        message = self.shorten(metadata['output_message'])
        
        print "Sending via twitter to %s: %s" % (metadata['twitter_name'], message)
        self.block_til_sent(lambda: self.twitter.direct_messages.new(user=twitter_id, text=message))
    

    def shorten(self, message):
        message = message.replace("\n", "")
        msg_len = self.max_length
        if len(message) > msg_len:
            message = message[0:msg_len - 3] + '...'
        return message
    
    def run(self):
        import time

        while self.__running:
            try:
                direct_messages = self.block_til_sent(self.twitter.direct_messages)
                for dm in direct_messages:
                    print dm
                    
                    m = {}
                    m['incoming_message'] = dm['text']
                    
                    sender = dm['sender']
                    m['fullname'] = sender['name']
                    m['twitter_id'] = sender['id']
                    m['twitter_name'] = sender['screen_name']
                    m['tz_offset'] = self.find_tz_offset(sender['time_zone'], sender['utc_offset'])
                    
                    try:
                        # this may or may not work
                        m['message_datetime_local'] = datetime.strptime(dm['created_at'], "%a, %d %b %Y %H:%M:%S +0000")        
                    except:
                        # Value Error
                        # by default, we'll use "now" as the reference time.
                        pass
                    
                    self.__listener(m)
                    
                    self.block_til_sent(lambda: self.twitter.direct_messages.destroy(id=dm['id']))
            except:
                import traceback
                traceback.print_exc()

            t = 0
            while t < self.delay and self.__running:
                time.sleep(5)
                t = t + 5
      
    def find_tz_offset(self, city, default):
        import pytz
        import datetime
        
        
        tz_names = [n for n in pytz.all_timezones if n.find(city)>=0]
        if len(tz_names) == 0:
            return default
        
        tz = pytz.timezone(tz_names[0])
        dt = datetime.datetime.now(tz=tz)
        td = dt.utcoffset()
        
        return td.seconds
        
        
        
      
    def block_til_sent(self, fn):
        backoff = self._time_delay()
        
        while self.__running:
            try:
                return fn()
            except:
                import traceback
                traceback.print_exc()
                e = sys.exc_info()[0]
                print "Will try again in %s seconds"

                t = 0
                delay = backoff.next()
                while t < delay and self.__running:
                    time.sleep(5)
                    t = t + 5
        
    def _time_delay(self):
        delays = [60, 120, 120, 300, 300, 600, 1800]
        i = 0
        while True:
            yield delays[i]
            i = (i + 1) % len(delays)
    def close(self):
        self.__running = False