# Class: SendEmails
# This class sends reminders, daily digests, and confirmations

class SendEmail:
	### Public Variables ###

	# None

	### Private Variables ###

	# Variable: howOftenSend
	# How often we're sending emails, in minutes.
	howOftenSend = 3;


	### Public Methods ###

	# Method: __init__
	# Queries <Database.reminders> to retrieve reminders which haven't been
	# sent and whose reminderTime (in the database) is less than the current
	# timestamp, plus <howOftenSend> minutes. Creates <Event> objects for each
	# event and passes the objects (one at a time) to <sendReminder>. After a
	# reminder has been sent, the reminderSent field in the database is set
	# to true.
	#
	# This also calls <Database.users> to retrieve the users who want reminders
	# to be sent within the next <howOftenSend> minutes. Passes the user IDs
	# (one at a time) to <sendDigest>.
	#
	# Parameters:
	#   None
	def __init__(self, email):

	# Method: sendReminder
	# Parses compiles the information in *event* into an email, and sends it.
	#
	# Parameters:
	#   event - <Event> object
	#
	# Returns:
	#   Nothing
	def sendReminder(self, event):


	# Method: sendDigest
	# Looks up all events belonging to *userID* which will occur within
	# days4digest (in the database) days from now.
	#
	# Parameters:
	#   userID - (int) ID of the user
	#
	# Returns:
	#   Nothing
	def sendDigest(self, userID):


	### Private Methods ###

	# None
