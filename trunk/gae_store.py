# Google App Engine implementation of Sandy's Back storage functionality, as
# abstractly specified in the store and entity modules

import logging

from google.appengine.ext import db

import entity
import search
import store


class User(db.Model):

  def __init__(self, *a, **k):
    theid = k.pop('theid', None)
    _from_entity = k.pop('_from_entity', False)
    try:
      self.u = entity.User(**k)
    except TypeError, e:
      raise RuntimeError("User init w: a=%s, k=%s, TypeError %s" % (a, k, e))
    if theid is not None:
      self.u.theid = theid
    db.Model.__init__(self, theid=self.u.theid, name=self.u.name,
        from_email=self.u.from_email, to_email=self.u.from_email,
        timezone_name=self.u.timezone_name,
        date_format=self.u.date_format, time_format=self.u.time_format,
        daily_digest_offset=self.u.daily_digest_offset,
        days_in_digest=self.u.days_in_digest,
        _from_entity=_from_entity)

  def nickname(self):
    return self.name

  theid = db.IntegerProperty(required=True)
  name = db.StringProperty(required=True)
  from_email = db.EmailProperty(required=True)
  to_email = db.EmailProperty(required=True)
  timezone_name = db.StringProperty(required=True)
  date_format = db.StringProperty(required=True)
  time_format = db.StringProperty(required=True)
  daily_digest_offset = db.IntegerProperty(required=True)
  days_in_digest = db.IntegerProperty(required=True)


class Event(search.SearchableModel):

  def __init__(self, *a, **k):
    theid = k.pop('theid', None)
    _from_entity = k.pop('_from_entity', False)
    self.e = entity.Event(**k)
    if theid is not None:
      self.e.theid = theid
    dd = dict(self.e.__dict__)
    dd.pop('self', None)
    search.SearchableModel.__init__(self, _from_entity=_from_entity, **dd)

  theid = db.IntegerProperty(required=True)
  reminder_sent = db.BooleanProperty()
  reminder_time = db.DateTimeProperty()
  repeat_interval = db.IntegerProperty(verbose_name="Repeat after N seconds")
  event_time = db.DateTimeProperty()
  all_day = db.BooleanProperty()
  name = db.StringProperty()
  description = db.TextProperty(required=True)
  tags = db.StringListProperty()      # might be empty!
  user = db.ReferenceProperty(User, required=True)


class Store(store.Store):
  """Implements needed methods for a GAE store w/the above models/entities.
  """
  # no overrides needed here, actualy: the base-class's no-ops are fine!


class Events(store.Events):
   """Represents a "table" with all the Events in the system."""

   def add(self, event):
     """Add to the store an entity.Event instance (with its specified User)."""
     event.put()

   def update(self, event):
     """Update an Event that must already be present in the store."""
     event.put()

   def delete(self, event):
     """Delete an Event that must have been present in the store."""
     event.delete()

   def textSearch(self, text, user=None):
     """Get events from the store matching the words in the text (& user).

     When user is not specified, events for any user are returned.
     The word-matching may/should use stemming, case insensitivity, &c. text may
     be a str (space-separated words, punctuation ignored) or list of words."""
     # TODO: stemming &c (this is pretty dumb;-)
     if isinstance(text, list):
       text = ' '.join(text)
     query = Event.all().search(text)
     if user is not None:
       query = query.filter("user =", user)
     res = list(query)
     logging.info('L %r -> %d', text, len(res))
     return res

   def timeSearch(self, time1=None, time2=None, user=None, pending_only=False):
     """Get events from the store scheduled for time1 <= t < time2 (& user).

     Omitted constraints are not applied, e.g. when time1 is None all events
     scheduled before time2 for the user are returned.

     If pending_only is True, only events still "pending" (not triggered yet)
     are returned. ALSO: pending_only implies using reminder time, otherwise
     the event time is used.
     """
     query = Event.all()
     if pending_only:
       field = "reminder_time"
       query = query.filter("reminder_sent =", False)
     else:
       field = "event_time"

     if time1 is not None:
       query = query.filter("%s >=" % field, time1)
     if time2 is not None:
       query = query.filter("%s <" % field, time2)
     if user is not None:
       query = query.filter("user =", user)
     res = list(query)
     logging.info('L %r, %r, %r, %r -> %d', time1, time2, user, 
                                            pending_only, len(res))
     return res

# TODO(somebody!): finish the rest...;-)

   def tagSearch(self, tags, any=False):
     """Get events from the store with any or all the given tags.

     tags is an array of str tags; when any is False, all must match."""

   def idSearch(self, theid):
     """Get event with given theid str, or None if no such event."""

   def generalSearch(self, queries, user=None, any=False):
     """General search for events based on a list of single-field queries.

     When user is specified, an AND with the user is added.  When any is false,
     all queries must match (AND), else any one of them (OR) [but the user
     constraint is always in AND with the others].

     Each query in the queries list is a str of a form such as "fieldname =
     value", or "fieldname < value", or "fieldname LIKE value%", and so on.

     Raises exceptions for syntax errors, too-complex queries, &c."""


class Users(store.Users):
   """Represents a "table" with all the Users in the system."""
   # hack to test w/o real user functionality yet
   @staticmethod
   def getit():
     query = User.all()
     user = query.get()
     if user is None:
       user = User(name="Santa", 
                   from_email="santa@north.pole",
                   to_email="sandy+santa@sandysback",
                   timezone_name="US/Pacific",
                   date_format="%Y-%m-%d",
                   time_format="%H:%M:%S",
                   daily_digest_offset=10*60*60,
                   days_in_digest=1)
       user.put()
     return user
 
   def __init__(self, store):
     """Start Users up with an already-connected Store."""

   def add(self, user):
     """Add to the store an entity.User instance."""

   def update(self, user):
     """Update an User that must already be present in the store."""

   def delete(self, user):
     """Delete an User that must have been present in the store."""

   def emailSearch(self, email):
     """Get the User with the specified email, or None."""

   def dailyDigestsSearch(self, time):
     """Get users wanting daily digests at < time who haven't had one yet today.

     Also marks the given time as the "time of last daily digest" for the users
     it returns."""

