import logging
import os
import wsgiref.handlers

from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext import webapp

import models
import search

def current_user():
  if 'USER' in os.environ:
    return users.User(os.environ['USER'] + '@sandysback.com')
  else:
    user = users.get_current_user()
    if user is None:
      user = users.User('tester@sandysback.com')
    return user

def do_logout():
  try: return users.create_logout_url('/')
  except AssertionError: return '/'

def main_respond(resp, content=''):
  resp.headers['Content-Type'] = 'text/html'
  resp.out.write('<html><head><title>Sand 1 Main</title></head><body>\n')
  resp.out.write('<p>Hi, %s  ' % current_user().nickname())
  resp.out.write(' (<a href="%s">Logout</a>)</p>' % do_logout())
  resp.out.write('<form action="/" method="get">\n')
  resp.out.write('<p>%s</p>\n' % content)
  resp.out.write('<p>\n')
  resp.out.write('<label for="do">What to do:</label>\n')
  resp.out.write('<input type="text" id="do" name="do">\n')
  resp.out.write('<input type="submit" value="Do"></p>\n')
  resp.out.write('</form>')
  resp.out.write('<p>\n')
  resp.out.write('<p>\n')


def bare_respond(resp, content=''):
  resp.headers['Content-Type'] = 'text/html'
  resp.out.write('<html><head><title>Sand 1 Barebones</title></head><body>\n')
  resp.out.write('<p>Hi, %s  ' % current_user().nickname())
  resp.out.write(' (<a href="%s">Logout</a>)</p>' % do_logout())
  resp.out.write('<p>%s</p>\n' % content)
  resp.out.write('<p>\n')
  resp.out.write('<form action="/" method="get">\n')
  resp.out.write('<label for="search">Look for:</label>\n')
  resp.out.write('<input type="text" id="search" name="search">\n')
  resp.out.write('<input type="submit" value="Search"></p>\n')
  resp.out.write('</form>')
  resp.out.write('<p>\n')
  resp.out.write('<form action="/" method="post">\n')
  resp.out.write('<label for="create">Create:</label>\n')
  resp.out.write('<input type="text" id="create" name="create">\n')
  resp.out.write('<input type="submit" value="Create"></p>\n')
  resp.out.write('</form>')


def store(phrase):
  """Store a phrase as a new fact.

  Args:
    phrase: a str with space-separated words
  Returns:
    a str confirming it's remembering the new fact
  """
  entity = models.Fact()
  entity.stuff = phrase
  entity.user = current_user()
  entity.put()
  logging.info('R %r', phrase)
  return "OK, remembering: %r" % phrase


def fetch(phrase):
  """Fetch all facts containing all words in phrase.

  Args:
    phrase: a str with space-separated words
  Returns:
    a list of str with all the facts containing all the words in phrase
  """
  query = models.Fact.all().search(phrase).filter(
              "user =", current_user())
  res = [(f.stuff, f.key()) for f in query]
  logging.info('L %r -> %d', phrase, len(res))
  return res

def getkey(verb, rest, req):
  if not rest.startswith('#'):
    return None, "Sorry, invalid arg %r for verb %s" % (rest, verb)
  try:
    num = int(rest[1:])
  except ValueError:
    return None, "Sorry, invalid number %r for verb %s" % (rest[1:], verb)
  key = req.get('ZZ%s' % num, '')
  if not key:
    return None, "Sorry, no number %r in previous list" % num
  return key, None


def parse(phrase, req):
  """Parse and execute the phrase (first word is the "verb").

  Args:
    phrase: a str with space-separated words
  Returns:
    a str or list of str with the result of the parsing + execution
  """
  p = phrase.lower()
  try:
    first_word, rest = p.split(None, 1)
  except ValueError:
    first_word, rest = p, ''
  else:
    if first_word in ('r', 'remember', 'remind'):
      return store(rest)
    elif first_word in ('l', 'lookup'):
      return fetch(rest)
    elif first_word in ('z', 'zaza'):
      key, msg = getkey('zaza', rest, req)
      if key is None:
        return msg
      entity = db.get(db.Key(key))
      return [(entity.stuff, entity.key())]
    elif first_word in ('f', 'forget'):
      key, msg = getkey('forget', rest, req)
      if key is None:
        return msg
      entity = db.get(db.Key(key))
      msg = "OK, forgotten %r" % entity.stuff
      entity.delete()
      return msg

  return "Sorry, don't understand %r for %r" % (first_word, rest)


class MainPage(webapp.RequestHandler):

  def get(self):
    stuff = self.request.get('do')
    if not stuff:
      main_respond(self.response, "What do you want to do?")
    else:
      result = parse(stuff, self.request)
      if isinstance(result, list):
        if result:
          lines = ['Found %d:' % len(result)]
          for i, (stuff, key) in enumerate(result):
            lines.append('<input type="hidden" name="ZZ%s" value="%s"> '
                         '#%s %s' % (i+1, key, i+1, stuff))
          result = '<br>\n'.join(lines)
        else:
          result = "Oops, found no relevant facts."
      main_respond(self.response, result)


class BarePage(webapp.RequestHandler):
  def post(self):
    # create a fact
    stuff = self.request.get('create')
    entity = models.Fact()
    entity.stuff = stuff
    entity.put()
    bare_respond(self.response, "Created fact: %s<br>" % stuff)

  def get(self):
    stuff = self.request.get('search')
    if not stuff:
      bare_respond(self.response, "What stuff are you looking for?")
    else:
      # Search the 'Person' Entity based on our keyword
      query = search.SearchableQuery('Fact')
      query.Search(stuff)
      res = []
      n = 0
      for result in query.Run():
         res.append(result['stuff'])
         n += 1
      res.insert(0, "Found %d:" % n)
      bare_respond(self.response, "<br>\n".join(res))


def application():
  return webapp.WSGIApplication([('/', MainPage),
                                 ('/bare', BarePage),
                                ],
                                debug=True)

def main():
  app = application()
  wsgiref.handlers.CGIHandler().run(app)

if __name__ == "__main__":
  main()

