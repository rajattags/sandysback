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
	# Initializes connection to SMTP server. Calls <DataStore.reminderTimeSearchEvents>
	# to retrieve events which need reminders sent prior to the current time, plus
	# <howOftenSend> minutes. Passes the returned <Event> objects (one at a time) to
	# <sendReminder>. After a reminder has been sent, the reminderSent field in the
	# database is set to true.
	#
	# This also calls <DataStore.digestTimeSearchUsers> to retrieve the users
	# who want daily digests send within the next <howOftenSend> minutes.
	# Passes the returned <User> objects (one at a time) to <sendDigest>.
	#
	# Parameters:
	#   None
	def __init__(self, email):


	# Method: __del__
	# Does nothing for now
	#
	# Parameters:
	#   None
	def __del__(self):


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
	# days4digest (in the database) days from now. Sends email to user.
	#
	# Parameters:
	#   userID - (int) ID of the user
	#
	# Returns:
	#   Nothing
	def sendDigest(self, userID):


	### Private Methods ###

	# None
