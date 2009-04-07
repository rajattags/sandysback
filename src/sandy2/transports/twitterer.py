import twitter

class TwitterListener(object):
   def __init__(self, username=None, password=None, delay=120):
      self.username = username
      self.password = password
      self.delay = delay
      self.__running = True

   def run(self):
      from threading import Thread
      import twitter
      import time

      while self.__running:
         api = twitter.Api(self.username, self.password)
         dms = api.GetDirectMessages()
         if len(dms):
            print "found %s new direct messages" % (len(dms))
         for dm in dms:
            #api.DestroyDirectMessage(dm.id)
            yield dm

         if self.__running:
            time.sleep(self.delay)
   
   def close(self):
      self.__running = False
