# Class: Event
# Provides easy access to properties of an event from a natural language string

class Event:
	### Public Variables ###

	# Variable: eventTime
	# *int:* (public) Unix timestamp of the time the event occurs
	eventTime = '';

	# Variable: beforeRemind
	# *int:* (public) Seconds before <time> a reminder is to be sent
	beforeRemind = '';

	# Variable: allDay
	# *bool:* (public) True = all day event. False = otherwise.
	allDay = '';

	# Variable: eventName
	# *string:* (public) Name of the event
	eventName = '';

	# Variable: description
	# *string:* (public) Further event details
	description = '';

	# Variable: tags
	# *list of strings:* (public) List containing the tags assiciated with this event
	tags = '';

	# Variable: repeat
	# *string:* (public) If this event repeats, repeat has the format
	# "(number) (hours/days/months/years)" For instance, "2 days" means
	# repeat every other day. "1 year" means repeat annually.
	# repeat = None if event does not repeat
	repeat = '';

	# Variable: weekdayRepeat
	# *bool:* (public) The weekday on which this event takes place.
	# (i.e., if the original date is the 2nd Tuesday in Mach and
	# "repeat" is equal to "1 month", the next occurrence is the
	# 2nd Tuesday in April).
	# weekdayRepeat = None if event does not repeat, if the event
	# repeats based on the actual date, not the weekday.
	#
	# For this release weekdayRepeat is always equal to None.
	weekdayRepeat = '';

	# Variable: id
	# *int:* (public) The id of the event. This variable may be set
	# to None. The only class which should read or write this 
	# variable is <Database>. <Event> objects returned by
	# Database.lookupEvents> will have id values, and
	# <Database.updateEvent> and <Database.deleteEvent>
	# will look at <Event>s' id values.
	id = '';


	### Private Variables ###

	# None


	### Public Methods ###

	# Method: __init__
	# Sets the public variables to what this method can parse from *message*.
	# Sets variable(s) to None if that part of the event is not present.
	#
	# Parameters:
	#   message - (string) raw email
	def __init__(self, message):

	
	# Method: __init__
	# Sets the public variables to the arguments passed to this method.
	#
	# Parameters:
	#   eventTime - <eventTime>
	#   beforeRemind - <beforeRemind>
	#   allDay - <allDay>
	#   eventName - <eventName>
	#   description - <description>
	#   tags - <tags>
	#   repeat - <repeat>
	#   weekdayRepeat - <weekdayRepeat>
	def __init__(self, eventTime, beforeRemind, allDay, eventName, description, tags, repeat, weekdayRepeat):


	### Private Methods ###

	# None
