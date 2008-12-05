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


	# Method: __del__
	# Disconnects from the database
	#
	# Parameters:
	#   None
	def __del__(self):


	# Method: addEvent
	# Adds an event to the database
	#
	# Parameters:
	#   event - <Event> object containing information about the event we wish to add
	# 
	# Returns:
	#   Nothing
	def addEvent(event):


	# Method: textSearchEvents
	# Receives a pattern string and returns all events whose name and/or description
	# matches the pattern. For queries with wildcards, use "*". This method will
	# translate "*" into the appropriate syntax for the database we're using.
	#
	# Parameters:
	#   pattern - (string) Text we're searching for. This method accepts the wildcard "*"
	#                    and translates it into the appropriate syntax for the database
        #                    we're using.
	#
	# Reuturns:
	#   events - list of <Event> objects.
	def textSearchEvents(pattern):


	# Method: timeSearchEvents
	# Returns events whose timestamp is between time1 and time2.
	#
	# Parameters:
	#   time1 - (int) Search for events occuring after this timestamp
	#   time2 - (int) Search for events occuring before this timestamp
	#   user - (<User>) Only return events belonging to this user. If this argument
	#          is left blank, events for all users are returned.
	#
	# Reuturns:
	#   events - list of <Event> objects.
	def timeSearchEvents(time1, time2, user=None):


	# Method: reminderTimeSearchEvents
	# Returns events whose reminders have not been sent and whose timestamp less than time.
	#
	# Parameters:
	#   time - (int) Search for events occuring before this timestamp
	#   user - (<User>) Only return events belonging to this user. If this argument
	#          is left blank, events for all users are returned.
	#
	# Reuturns:
	#   events - list of <Event> objects.
	def reminderTimeSearchEvents(time, user=None):


	# Method: tagSearchEvents
	# Returns events which match specific tags
	#
	# Parameters:
	#   tags - (list of strings) Tags this event must match
	#   any - (bool) If true, searches for events which match *any* of the tags in the
	#         array. Else, searches for events which match *all* of the tags (default).
	#
	# Reuturns:
	#   events - list of <Event> objects.
	def tagSearchEvents(tags, any=false):


	# Method: idSearchEvents
	# Returns event whose id is equal to *id*.
	#
	# Parameters:
	#   id - (string) id of the event we wish to find
	#
	# Reuturns:
	#   event - <Event> object containing the information about the event we found.
	#           event=None if no such event was found.
	def idSearchEvents(id):


	# Method: searchEvents
	# Use this method in the event that you want to search through fields not accessible
	# using the other event searching methods. (e.g., if you wanted to find all "all-day"
	# events)
	#
	# Parameters:
	#   queries - 2-dimensional list formatted in the following manner:
	#
	#             [ [fieldName, matchPattern], [fieldName, matchPattern], ... ]
	#
	#             where fieldName is the name of the field and matchPattern is the text
	#             we're searching for, which can include the "*" wildcard.
	#
	#   any - (bool) If true, searches for events which match *any* of the queries.
	#         Else, searches for events which match *all* of the tags (default).
	#
	# Reuturns:
	#   events - list of <Event> objects.
	def searchEvents(queries, any=false):


	# Method: updateEvent
	# Updates an event based on an <Event> object this method receives. We find the event
	# in the database which has the id <Event.id> and update all the fields in the database
	# pertaining to this event with the information contained in the respective public
	# variables of *event*.
	#
	# Parameters:
	#   event - <Event> object
	# 
	# Returns:
	#   Nothing
	def updateEvent(event):


	# Method: deleteEvent
	# Deletes an event
	#
	# Parameters:
	#   event - <Event> (the event to delte from the database)
	# 
	# Returns:
	#   Nothing
	def deleteEvent(event):


	# Method: addUser
	# Adds a user to the database
	#
	# Parameters:
	#   user - <User> object containing the information about the user we wish to add
	# 
	# Returns:
	#   Nothing
	def addUser(user):


	# Method: emailSearchUser
	# Returns a <User> object which matches the user's email address
	#
	# Parameters:
	#   emailAddress - (string) the email address of the user we wish to find
	# 
	# Returns:
	#   user - <User> object containing the information about the user we found.
	#          user=None if no such user was found.
	def emailSearchUser(user):


	# Method: digestTimeSearchUsers
	# Returns users who have not yet received a daily digest today, and want their daily
	# digest sent prior to a specified time. That is, return users whose "dailyDigest"
	# fields (in the database) is less than the argument *time*. This method also updates
	# the "digestSent" field in the database with a timestamp pointing to today at midnight
	# (where "today" is defined by UTC)
	#
	# Parameters:
	#   time - (int) Number of seconds after midnight. Search for users whose daily digest
	#          time is les than this value
	#
	# Reuturns:
	#   users - list of <User> objects.
	def digestTimeSearchUsers(time):
	

	# Method: updateUser
	# Updates an user based on a <User> object this method receives. We find the user
	# in the database which has the id <User.id> and update all the fields in the database
	# pertaining to this user with the information contained in the respective public
	# variables of *user*.
	#
	# Parameters:
	#   user - <User> object
	# 
	# Returns:
	#   Nothing
	def updateUser(user):


	# Method: deleteUser
	# Deletes an user
	#
	# Parameters:
	#   user - <User> (the user to delte from the database)
	# 
	# Returns:
	#   Nothing
	def deleteUser(user):



	### Private Methods ###

	# None

