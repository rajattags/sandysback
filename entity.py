# Entity models for Sandy's Back storage functionality


class Event(object):
   """Represents an event (or "fact"...) in the system w/a unique ID."""

   highest_id = 999999    # highest event ID used so far

   def __init__(self, reminder_time=None, repeat_interval=None, event_time=None,
                all_day=False, name=None, description=None,
                tags=None, user=None, reminder_sent=False):
     """Initialize an event; fields can be None, or...:
     reminder_time: timestamp (seconds since epoch) at which to send reminder
     repeat_interval: seconds after reminder_time before next reminder (if any)
     event_time: timestamp FOR which reminder is being sent
     all_day: bool, True for all-day events
     name, description: two strings (description is the only mandatory field!)
     tags: list of strings
     user: entity.User instance owning this event.
     reminder_sent:   bool, True if the reminder was sent

     The event also has one internally-generated instance attribute:
     theid:           an arbitrary unique ID

     All the time-related attributes can be None to make a so-called ``event''
     which is actually a "fact" to remember (no reminders scheduled, etc).
     """
     assert description is not None
     if tags is None:
       tags = []
     Event.highest_id += 1
     self.theid = Event.highest_id
     self.__dict__.update(locals())
     self.reminder_sent = False


class User(object):
   """Represents a user of the system w/a unique ID."""

   highest_id = 99999    # highest user ID used so far

   def __init__(self, name, from_email, to_email, timezone_name, date_format,
                time_format, daily_digest_offset, days_in_digest=1):
     """Initialize a user; fields can be None, or...:
     name: str, user's full name
     from_email: user's own email address
     to_email: address user will be sending mail to for Sandy
     timezone_name: valid timezone name to determine offset, dst, etc
     date_format: strftime format string for dates
     time_format: strftime format string for times
     daily_digest_offset: offset in seconds from midnight UTC for daily digest
     days_in_digest: how many days to summarize in a daily digest

     The user also has two more instance attributes:
     theid:           an arbitrary unique ID
     digest_sent:     timestamp when a digest was last sent, or None
     """
     User.highest_id += 1
     self.theid = User.highest_id
     self.name = name
     self.from_email = from_email
     self.to_email = from_email
     self.timezone_name = timezone_name
     self.date_format = date_format
     self.time_format = time_format
     self.daily_digest_offset = daily_digest_offset
     self.days_in_digest = days_in_digest
     self.digest_sent = False

