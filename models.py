from google.appengine.ext import db
import search

class Fact(search.SearchableModel):
  stuff = db.TextProperty()
  # tags = db.TextProperty()
  publishDate = db.DateTimeProperty(auto_now_add=True)

