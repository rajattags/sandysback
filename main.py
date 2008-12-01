import logging
import wsgiref.handlers
from google.appengine.ext import webapp
import search

import models

def main_respond(resp, content=''):
  resp.headers['Content-Type'] = 'text/html'
  resp.out.write('<html><head><title>Sand 1 Main</title></head><body>\n')
  resp.out.write('<p>%s</p>\n' % content)
  resp.out.write('<p>\n')
  resp.out.write('<form action="/" method="get">\n')
  resp.out.write('<label for="do">What to do:</label>\n')
  resp.out.write('<input type="text" id="do" name="do">\n')
  resp.out.write('<input type="submit" value="Do"></p>\n')
  resp.out.write('</form>')
  resp.out.write('<p>\n')
  resp.out.write('<p>\n')


def bare_respond(resp, content=''):
  resp.headers['Content-Type'] = 'text/html'
  resp.out.write('<html><head><title>Sand 1 Barebones</title></head><body>\n')
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
  query = search.SearchableQuery('Fact')
  query.Search(phrase)
  res = [f['stuff'] for f in query.Run()]
  logging.info('L %r -> %d', phrase, len(res))
  return res


def parse(phrase):
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
  return "Sorry, don't understand %r for %r" % (first_word, rest)


class MainPage(webapp.RequestHandler):

  def get(self):
    stuff = self.request.get('do')
    if not stuff:
      main_respond(self.response, "What do you want to do?")
    else:
      result = parse(stuff)
      if isinstance(result, list):
        if result:
          result.insert(0, 'Found %d:' % len(result))
          result = '<br>'.join(result)
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

