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


	# Variable: userEmail
	# *string:* (public) The id of the user who owns this event
	#
	# For this release weekdayRepeat is always equal to None.
	userEmail = '';


	# Variable: reminderSent
	# *bool:* (public) True if a reminder has been sent for this event. False if otherwise.
	reminderSent = '';


	# Variable: id
	# *int:* (public) The id of the event. This variable may be set
	# to None. The only class which should read or write this 
	# variable is <Database>. <Event> objects returned by
	# <Database>'s searching methods will have id values and
	# <Database.updateEvent> and <Database.deleteEvent>
	# will look at id values.
	id = '';


	### Private Variables ###

	# None


	### Public Methods ###

	# Method: __init__
	# If only one argument is passed in, *arg1* is a message which contains information
	# about this event, in regular human syntax, which must be parsed.
	#
	# If more than one argument is passed in, <eventTime> is set to value of *arg1*, and
	# all the remaining public variables are set to the arguments passed to this function
	# which have the same name. If any arguments not set are set, the respective public
	# variables are set to None.
	#
	# Parameters:
	#   arg1
	#        - *if no other arguments are provided:* (string) message containing information about this event.
	#        -  *Otherwise:* (int) value of arg1 is copied into <eventTime>
	#
	#   beforeRemind - (int) value copied into <beforeRemind>
	#   allDay - (bool) value copied into <allDay>
	#   eventName - (string) value copied into <eventName>
	#   description - (string) value copied into <description>
	#   tags - (string) value copied into <tags>
	#   repeat - (string) value copied into <repeat>
	#   weekdayRepeat - (string) value copied into <weekdayRepeat>
	def __init__(self, arg1, eventTime=None, beforeRemind=None, allDay=None, eventName=None, description=None, tags=None, repeat=None, weekdayRepeat=None, id=None):


	# Method: __del__
	# Does nothing for now
	#
	# Parameters:
	#   None
	def __del__(self):


	### Private Methods ###

	# None
