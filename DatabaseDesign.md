# Database Design #

Below is a proposed database design.

NOTE: Fields of type "timestamp" are actually integers whose values should be UNIX timestamps. In MySQL, there is a field type called "timestamp" which does something different. Also, please note that all times are in UTC, even when this is not explicitly stated.


## TABLE: Reminders ##

| **eventTime (timestamp)** |
|:--------------------------|

This column is the Unix Timestamp for the time in which the event takes place. For those who aren't familiar, the Unix timestamp is the number of seconds elapsed since January 1, 1970, and is the accepted format for "raw" (unformatted, computer-readable) dates. The Unix Timestamp is ALWAYS in UTC (i.e., the time according to Greenwich)

**NOTE:** For "all day" events, eventTime will be equal to midnight of that particular day, in the user's time zone.


| **beforeRemind (timestamp)** |
|:-----------------------------|

The number of seconds before "eventTime" the reminder is to be set.

**NOTE:** This is seconds just to make the math easier... so that eventTime - beforeRemind is the Unix time of when to send the reminder

**NOTE:** This value can be negative. If the user has an all-day event and wants to be reminded at 10:00pm the previous day, this value will be positive. But if the user wants to be reminded at 7:00am the day of the event, this value will be negative (because the reminder is sent **after** the event time, which occurs at midnight)


| **reminderTime (timestamp)** |
|:-----------------------------|

The actual time the reminder is to be sent (again, in UTC). This field is simply equal to eventTime - beforeRemind. This table will be sorted by reminderTime so that we can have a cron job which grabs events whose reminderTime is between the current time and 5 minutes (or whatever we end up deciding) from now.

**NOTE:** eventTime, beforeRemind, and reminderTime are all NULL if no time is associated with this "event"


| **allDay (boolean)** |
|:---------------------|

True = all day event. False = otherwise.


| **eventName (varchar)** |
|:------------------------|

What the user has decided to name this event.

| **details (varchar)** |
|:----------------------|

This is what Sandy calls "context."


| **tags (varchar)** |
|:-------------------|

All lowercase, space delimited


| **repeat (varchar)** |
|:---------------------|

NULL if this event does not repeat. Otherwise, this field has the format "(number) (hours, days, months, years)" For instance, "2 days" means repeat every other day. "1 year" means repeat annually.

**NOTE:** Once an event has passed, if repeat=NULL, nothing happens, and our cron jobs never look at past events, so life moves on happily. However, if repeat is not NULL, once the event passes, eventTime and reminderTime will be updated to increment the timestamp to some time in the future by the value of "repeat"


| **weekdayRepeat (varchar)** |
|:----------------------------|

The weekday on which this event takes place. (i.e., if the original date is the 2nd Tuesday in Mach and "repeat" is equal to "1 month", the next occurrence is the 2nd Tuesday in April).

**NOTE:** For most events, weekdayRepeat will be NULL (i.e., just look at the actual date of the event, forget what weekday it's on). We probably won't use this field until version 2.0. (i.e., for now, it's always NULL).


| **user (foreign key from "users" table)** |
|:------------------------------------------|

We use this to link this event to a particular user. See users table (below).


| **reminderSent (boolean)** |
|:---------------------------|

Default = False (reminder not sent yet). Set to true when reminder has been sent.


| **id (key)** |
|:-------------|



## TABLE: Users ##
| **name (varchar)** |
|:-------------------|

| **fromEmail (varchar)** |
|:------------------------|

Only accept emails from this address


| **toEmail (varchar)** |
|:----------------------|

Only accept emails sent to this address


| **timeZone (int)** |
|:-------------------|

Offset from UTC


| **dst (boolean)** |
|:------------------|

Does the user's timezone observe daylight savings time?


| **dateFormat (fixed char)** |
|:----------------------------|

UNIX _date_ FORMAT string. e.g.:
  * %m/%d/%y     (e.g., 1/20/2008)
  * %d/%m/%y     (e.g., 20/1/2008)
  * %m.%d.%y     (e.g., 1.20.2008)
  * %d.%m.%y     (e.g., 20.1.2008)
  * %B %d, %y    (e.g., Jan 20, 2008)
  * etc.


| **timeFormat (fixed char)** |
|:----------------------------|

UNIX _date_ FORMAT string. e.g.:
  * %H:%M     (e.g., 14:00)
  * %I:%M %p  (e.g., 2:00 PM)
  * etc.


| **dailyDigest (int)** |
|:----------------------|

Number of seconds after midnight the user wants the daily digest sent (in UTC). Can be negative if the user wants the daily digest sent before midnight, UTC. This field is NULL of the user doesn't want a daily digest sent.


| **digestSent (timestamp)** |
|:---------------------------|

timestamp pointing to midnight of the day the daily digest was sent. Set to 0 if the user doesn't want a daily digest.


| **days4digest (int)** |
|:----------------------|

Number of days to include on the daily digest (default=1)


| **id (key)** |
|:-------------|