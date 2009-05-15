import twitter

class TwitterListener(object):
   def __init__(self, hostname='twitter.com', username=None, password=None, delay=120):
      self.username = username
      self.password = password
      self.hostname = hostname
      self.delay = delay
      self.__running = True

   def run(self):
      from threading import Thread
      import twitter
      import time

      while self.__running:
         api = twitter.Api(username = self.username, password = self.password, twitterserver = self.hostname)
         dms = api.GetDirectMessages()
         if len(dms):
            print "found %s new direct messages" % (len(dms))
         for dm in dms:
            yield dm

         if self.__running:
            time.sleep(self.delay)
   
   def close(self):
      self.__running = False
