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
	# of each iteration. Depending on which keywords we find, we pass the <Email>
	# object to <newEvent>, <lookupEvents>, and/or <updateEvent>.
	#
	# Parameters:
	#   None
	def __init__(self, email):

	# Method: newEvent
	# Parses <Email.message> from *email* and creates an <Event>, which is passed to <Database.newEvent>
	#
	# Parameters:
	#   email - <Email> object
	#
	# Returns:
	#   Nothing
	def newEvent(self, email):


	# Method: lookupEvents
	# Parses <Email.message> from *email* and performs the appropriate <Database> call
	#
	# Parameters:
	#   email - <Email> object
	#
	# Returns:
	#   Nothing
	def lookupEvents(self, email):


	# Method: updateEvent
	# Parses <Email.message> to figure out which event listed in <Email.quote> the user wishes to update or delete.
	#
	# Parameters:
	#   email - <Email> object
	#
	# Returns:
	#   Nothing
	def updateEvent(self, email):


	### Private Methods ###

	#
