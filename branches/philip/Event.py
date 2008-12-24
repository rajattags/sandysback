# Class: Event
# Provides easy access to properties of an event from a natural language string

class Event:
	### Public Variables ###

	# Variable: user
	# *string:* (public) The id of the user who owns this event
	user = ''

	# Variable: eventTime
	# *int:* (public) Unix timestamp of the time the event occurs
	eventTime = ''

	# Variable: beforeRemind
	# *int:* (public) Seconds before <time> a reminder is to be sent
	beforeRemind = ''

	# Variable: allDay
	# *bool:* (public) True = all day event. False = otherwise.
	allDay = ''

	# Variable: eventName
	# *string:* (public) Name of the event
	eventName = ''

	# Variable: description
	# *string:* (public) Further event details
	description = ''

	# Variable: tags
	# *list of strings:* (public) List containing the tags assiciated with this event
	tags = []

	# Variable: repeat
	# *string:* (public) If this event repeats, repeat has the format
	# "(number) (hours/days/months/years)" For instance, "2 days" means
	# repeat every other day. "1 year" means repeat annually.
	# repeat = None if event does not repeat
	repeat = ''

	# Variable: weekdayRepeat
	# *bool:* (public) The weekday on which this event takes place.
	# (i.e., if the original date is the 2nd Tuesday in Mach and
	# "repeat" is equal to "1 month", the next occurrence is the
	# 2nd Tuesday in April).
	# weekdayRepeat = None if event does not repeat, if the event
	# repeats based on the actual date, not the weekday.
	#
	# For this release weekdayRepeat is always equal to None.
	weekdayRepeat = ''

	# Variable: reminderSent
	# *bool:* (public) True if a reminder has been sent for this event. False if otherwise.
	reminderSent = ''

	# Variable: id
	# *string:* (public) The id of the event. This variable may be set
	# to None. The only class which should read or write this 
	# variable is <Storage>. <Event> objects returned by
	# <Storage>'s searching methods will have id values and
	# <Storage.updateEvent> and <Storage.deleteEvent>
	# will look at id values.
	id = ''


	### Private Variables ###

	# None


	### Public Methods ###

	# Method: __init__
	# If we wish to create an event based on a string which  contains information
	# about this event (in regular human-readable syntax), only one argument is
	# provided in addition to *user*. Namely, *message* is the aforementioned string.
	#
	# If we wish to pass in all the necessary details as separate arguments, set
	# *message* to None and set the remaining arguments. The public variables will
	# be set to be equal to the respective arguments. If any arguments not set are set,
	# the respective public variables are set to None.
	#
	# Parameters:
	#   user - <user>
	#   message - (string) message containing information about this event
	#   eventTime -  <eventTime>
	#   beforeRemind - <beforeRemind>
	#   allDay - <allDay>
	#   eventName - <eventName>
	#   description - <description>
	#   tags - <tags>
	#   repeat - <repeat>
	#   weekdayRepeat - <weekdayRepeat>
	#   reminderSent - <reminderSent> (Defaults to False)
	#   id - <id>
	def __init__(self, user, message, eventTime=None, beforeRemind=None, allDay=None, eventName=None, description=None, tags=None, repeat=None, weekdayRepeat=None, reminderSent=False, id=None):

		self.user = user

		if message != None:
			parseMessage(message)
		else:
			self.eventTime = eventTime
			self.beforeRemind = beforeRemind
			self.allDay = allDay
			self.eventName = eventName
			self.description = description
			self.tags = tags
			self.repeat = repeat
			self.weekdayRepeat = weekdayRepeat
			self.reminderSent = reminderSent


	### Private Methods ###

	# Method: parseMessage
	# Parses the string *message* and assigns the class variables
	#
	# Parameters:
	#   message - (string) message containing information about this event

	def parseMessage(self, message):
		tags = []

		words = message.split()
		for w in words:
			if w.startswith('#'):
				tags.append(w)
				message.replace(w, '')

			# TODO: Parse other things from the message... like the date, etc.
			description = message
			self.tags = tags
