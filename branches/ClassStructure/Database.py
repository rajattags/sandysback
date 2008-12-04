# Class: Database
# Provides easy access to a database -- whether MySQL, App Engine, etc.

class Email:
	### Public Variables ###

	# None


	### Private Variables ###

	# None


	### Public Methods ###

	# Method: __init__
	# Connects to the database
	#
	# Parameters:
	#   None
	def __init__(self):


	# Method: addEvent
	# Adds an event to the database
	#
	# Parameters:
	#   event - <Event>
	# 
	# Returns:
	#   Nothing
	def addEvent(event):


	# Method: lookupEvents
	# Receives a query string and returns all events which match the query.
	# For queries with wildcards, use "*". This method will translate "*"
	# into the appropriate syntax for the database we're using.
	#
	# Parameters:
	#   query - (string) Text we're searching for. This method accepts the wildcard "*"
	#                    and translates it into the appropriate syntax for the database
        #                    we're using.
	#
	# Reuturns:
	#   events - array of <Event> objects
	def lookupEvents(query):


	# Method: updateEvent
	# Updates an event
	#
	# Parameters:
	#   origEvent - The original <Event> object
	#   updatedEvent - The updated <Event> object (the event to replace origEvent)
	# 
	# Returns:
	#   Nothing
	def updateEvent(origEvent, updatedEvent):


	# Method: deleteEvent
	# Deletes an event
	#
	# Parameters:
	#   event - <Event> (the event to delte from the database)
	# 
	# Returns:
	#   Nothing
	def deleteEvent(event):


	### Private Methods ###

	# None

