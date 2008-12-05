# Class: ReceiveEmails
# This class runs through all the emails in the inbox and acts on them appropriately

class ReceiveEmail:
	### Public Variables ###

	# None

	### Private Variables ###

	# None


	### Public Methods ###

	# Method: __init__
	# Connects to the email account, retrieves a list of messages in the inbox,
	# and loops through each email. Creates an <Email> object at the beginning
	# of each iteration. The <Email> object is passed to  <addEvent>, <lookupEvents>,
	# and <updateEvent>.
	#
	# Parameters:
	#   None
	def __init__(self, email):


	# Method: addEvent
	# Parses <Email.message> from *email* and creates an <Event>, which is passed to
	# <Database.addEvent>. Multiple (or no) events may be added, depending on how many
	# add-event instructions are found in the email. Sends confirmation email to the user.
	#
	# Parameters:
	#   email - <Email> object
	#
	# Returns:
	#   Nothing
	def addEvent(self, email):


	# Method: lookupEvents
	# Parses <Email.message> from *email* and calls <Database.textSearchEvents>, <Database.timeSearchEvents>, or <Database.tagSearchEvents>. Sends reply to the user.
	#
	# Parameters:
	#   email - <Email> object
	#
	# Returns:
	#   Nothing
	def lookupEvents(self, email):


	# Method: updateEvent
	# This method parses <Email.message> to figure out which event listed in <Email.quote>
	# the user wishes to update or delete. The event is retrieved by calling
	# <Database.idSearchEvents>. The returned <Event> object is modified and passed to
	# <Database.updateEvent>. Sends confirmation email to the user.
	#
	# Parameters:
	#   email - <Email> object
	#
	# Returns:
	#   Nothing
	def updateEvent(self, email):


	### Private Methods ###

	#
