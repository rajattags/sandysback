# Class: User
# This class contains information about a user

class User:
	### Public Variables ###

	# Variable: name
	# *string:* (public) The user's name
	name = ''

	# Variable: fromEmail
	# *string:* (public) The user's email address
	fromEmail = ''

	# Variable: toEmail
	# *string:* (public) The email address the user will send instructions to
	toEmail= ''

	# Variable: timeZone
	# *int:* (public) Offset from UTC (in seconds)
	timeZone = ''

	# Variable: dst
	# *bool:* (public) Does the user's timezone observe daylight savings time?
	dst = ''

	# Variable: dateFormat
	# *string:* (public) UNIX date FORMAT string. examples...
	# - %m/%d/%y (e.g., 1/20/2008)
	# - %d/%m/%y (e.g., 20/1/2008)
	# - %m.%d.%y (e.g., 1.20.2008)
	# - %d.%m.%y (e.g., 20.1.2008)
	# - %B %d, %y (e.g., Jan 20, 2008)
	# - etc. 
	dateFormat = ''

	# Variable: timeFormat
	# *string:* (public) UNIX date FORMAT string. examples...
	# - %H:%M (e.g., 14:00)
	# - %I:%M %p (e.g., 2:00 PM)
	# - etc. 
	timeFormat = ''

	# Variable: dailyDigestOffset
	# *int:* (public) Number of seconds after midnight the user wants the daily digest sent (in UTC).
	# Can be negative if the user wants the daily digest sent before midnight, UTC. This field is set
	# to None if the user doesn't want a daily digest sent. 
	dailyDigestOffset = ''


	# Variable: digestSent
	# *int:* (public) Timestamp pointing to midnight of the day the daily digest was sent.
	# Set to 0 if the user doesn't want a daily digest. 
	digestSent = ''


	# Variable: days4digest
	# *int:* (public) Number of days to include on the daily digest (default=1) 
	days4digest = ''


	# Variable: id
	# *string:* (public) The id of the user. This variable may be set
	# to None. The only class which should read or write this 
	# variable is <Storage>. <User> objects returned by
	# <Storage>'s searching methods will have id values and
	# <Storage.updateUser> and <Storage.deleteUser>
	# will look at id values.
	id = ''


	### Private Variables ###

	# None


	### Public Methods ###

	# Method: __init__
	# Sets the appropriate public variables
	#
	# Parameters:
	#   name - <name>
	#   fromEmail - <fromEmail>
	#   toEmail - <toEmail>
	#   timeZone - <timeZone>
	#   dst - <dst>
	#   dateFormat - <dateFormat>
	#   timeFormat - <timeFormat>
	#   dailyDigestOffset - <dailyDigestOffset>
	#   digestSent - <digestSent>
	#   days4digest - <days4digest>
	#   id - <id>
	def __init__(self, name, fromEmail, toEmail, timeZone, dateFormat, timeFormat, dailyDigestOffset, days4digest, id):
		self.name = name
		self.fromEmail = fromEmail
		self.toEmail = toEmail
		self.timeZone = timeZone
		self.dateFormat = dateFormat
		self.timeFormat = timeFormat
		self.dailyDigestOffset = dailyDigesOffsett
		self.days4digest = days4digest
		self.id = id
