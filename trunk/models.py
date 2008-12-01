from google.appengine.ext import db
import search

class Fact(search.SearchableModel):
  stuff = db.TextProperty()
  user = db.UserProperty()
  publishDate = db.DateTimeProperty(auto_now_add=True)

