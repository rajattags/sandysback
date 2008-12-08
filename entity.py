# Entity models for Sandy's Back storage functionality


class Event(object):
   """Represents an event (or "fact"...) in the system w/a unique ID."""

   highest_id = 999999    # highest event ID used so far

   def __init__(self, reminder_time, repeat_interval, event_time, all_day,
                name, description, tags, user):
     """Initialize an event; fields can be None, or...:
     reminder_time: timestamp (seconds since epoch) at which to send reminder
     repeat_interval: seconds after reminder_time before next reminder (if any)
     event_time: timestamp FOR which reminded is being sent
     all_day: bool, True for all-day events
     name, description: two strings
     tags: list of strings
     user: entity.User instance owning this event.

     The event also has two more instance attributes:
     theid:           an arbitrary unique ID
     reminder_sent:   timestamp when a reminder was last sent, or None
     """
     Event.highest_id += 1
     self.theid = Event.highest_id
     self.__dict__.update(locals())
     self.reminder_sent = None


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
     self.__dict__.update(locals())
     self.digest_sent = None

