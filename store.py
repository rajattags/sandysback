# abstract interfaces for Sandy's Back storage functionality, implicity based
# on the `entity' module (q.v.)

class Store(object):
  """Represents an underlying storage connection (+ cursor etc etc as needed).

  This base class offers no-op methods, subclasses override as needed.
  """
  def connect(self, *a, **k):
    """Establish a connection to the store, with whatever args are needed."""

  def begin(self):
    """Start a transaction, return an opaque ID for it."""

  def commit(self, transaction):
    """Commit a transaction (& all nested ones) given its ID."""

  def rollback(self, transaction):
    """Rollback a transaction (& all nested ones) given its ID."""

  def close(self):
    """Definitive termination of this connection."""


class Events(object):
   """Represents a "table" with all the Events in the system."""
   def __init__(self, store):
     """Start Events up with an already-connected Store."""

   def add(self, event, user=None):
     """Add to the store an entity.Event instance (maybe with a specified User).

     When user is not specified, the event itself must contain a valid user."""

   def update(self, event):
     """Update an Event that must already be present in the store."""

   def delete(self, event):
     """Delete an Event that must have been present in the store."""

   def textSearch(self, text, user=None):
     """Get events from the store matching the words in the text (& user).

     When user is not specified, events for any user are returned.
     The word-matching may/should use stemming, case insensitivity, &c. text may
     be a str (space-separated words, punctuation ignored) or list of words."""

   def timeSearch(self, time1=None, time2=None, user=None, pending_only=False):
     """Get events from the store scheduled for time1 <= t < time2 (& user).

     Omitted constraints are not applied, e.g. when time1 is None all events
     scheduled before time2 for the user are returned.

     If pending_only is True, only events still "pending" (not triggered yet)
     are returned."""

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


class Users(object):
   """Represents a "table" with all the Users in the system."""
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

