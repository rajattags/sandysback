# Class: Storage
# Provides easy access to a database -- whether MySQL, AppEngine, etc.

import logging

from google.appengine.ext import db

import search
import re
import User
import Event


class Storage(db.Model):
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
	#def __init__(self):


	# Method: __del__
	# Disconnects from the database
	#
	# Parameters:
	#   None
	#def __del__(self):


	# Method: storeEvent
	# Adds or updates  an event in the database
	#
	# Parameters:
	#   event - <Event> object containing information about the event we wish to add. If
	#           the <Event.id> class variable is set, and there exists an event with this
	#           id, the event passed to this function will replace the stored event
	#           (i.e., the event will be updated)
	# 
	# Returns:
	#   Nothing
	def storeEvent(self, event):
		if event.id == None:
			dbEvent = Storage.EventModel()
		else:
			dbEvent = db.get(event.id)

		dbEvent.name			= event.name
		dbEvent.fromEmail		= event.fromEmail
		dbEvent.toEmail			= event.toEmail
		dbEvent.timeZone		= event.timeZone
		dbEvent.dateFormat		= event.dateFormat
		dbEvent.timeFormat		= event.timeFormat
		dbEvent.dailyDigestOffset	= event.dailyDigesOffsett
		dbEvent.days4digest		= event.days4digest

		dbEvent.put()


	# Method: deleteEvent
	# Deletes an event
	#
	# Parameters:
	#   event - <Event> (the event to delete from the database)
	# 
	# Returns:
	#   Nothing
	def deleteEvent(self, event):
		dbEvent = db.get(event.id)
		dbEvent.delete()


	# Method: search
	# Accepts a SQL-like SELECT query for the EVENTS or USERS table.
	# Returns a list of <Event> or <User> objects which match the query.
	#
	# Accepted SQL query keywords:
	# - WHERE <field> {< | <= | > | >= | = | != | INCLUDES | IINCLUDES | LIKE } <value>
	#   - See notes below for information on INCLUDES, IINCLUDES, and LIKE.
	# - AND / AND WHERE (both are acceptable and interchangeable)
	# - ORDER BY field1[, field2, ...]
	# - LIMIT <limit>
	#   - Specifying both the limit and offset with a single LIMIT command is not
	#     supported. Use the OFFSET command. (e.g., LIMIT <limit> OFFSET <offset>)
	# - OFFSET <offset>
	# - UNION [ ALL | DISTINCT ]
	#   - Merges two SELECT queries.
	#   - DISTINCT is implied. Mixed use of ALL and DISTINCT works the same way as it
	#     does with MySQL.
	#
	# Notes: 
	#   - When passing in queries, you're responsible to make sure they work. This method
	#    will not fail gracefully if you have an error in your query.
	#   - Inserting a 'UNION' between the two SELECT statements is optional. The result of
	#    this query will be to query the database according to the two SELECT statements
	#    and merge the result, deleting duplicates... just like the MySQL UNION statement,
	#    except that sorting works slightly differently. Both queries will be sorted, then
	#    the results from the second query will be tacked onto those of the first query...
	#    with duplicates removed (unless 'ALL' is specified, in which case, duplicates will
	#    not be removed). Sorting works much better with the MySQL interface... so if you
	#    want sorting with UNION statements to work the way it does with MySQL, either use
	#    the MySQL interface or annoy Google into fixing their crappy database.
	#   - The statement 'field1 INCLUDES "value1 value2 value3"' returns fields which
	#    include the words value1, value2, and value3. These values are case sensitive.
	#    Use IINCLUDES for a case-insensitive search. Note that there is no substring search,
	#    so you can't search for fields which use the phrase "basketball game"... you can
	#    only search for fields which use both words "basketball" and "game". Again, this
	#    is because Google didn't bother to make a real database. If you use the MySQL
	#    interface, you can use the LIKE operator.
	#   - Use LIKE just as you would with MySQL. But it only works for MySQL because
	#    it's not fair to cripple the MySQL users simply because Google's database sucks.
	#    Please don't use it unless you *have to*. But it's here if you need it. And if you
	#    use it, make sure to *CLEARLY WARN* users that your code will cause Google to
	#    explode should they try to swap in the Google AppEngine interface while using
	#    your code.
	#   - JOIN is not supported because (1) I'm lazy, and (2) I want to encourage developers
	#    to create queries which work with both MySQL and Google AppEngine, with the
	#    exception of the LIKE statement because I view that as a necessity
	#   - No, I don't hate Google. I just think that AppEngine is severely lacking, and
	#    should not have been released until it was mature.
	#
	# Parameters:
	#   userQuery - Query written in our own query language (see above notes).
	# 
	# Returns:
	#   users - list of <Event> objects
	def search(self, userQuery):
		# queries is a 3-dimensional list containing information about the user's query.
		# This list has the following format:
		# queries = [ [ {'all' | 'distinct'}, table, orderBy, limit, offset, [field1, comparison1, value1], [field2, comparison2, value2], ... ], ... ]
		#
		# For example, suppose userQuery is equal to:
		# SELECT * FROM EVENTS WHERE field1=value1 AND field2>value2 ORDER BY sort1, sort2, LIMIT 10 OFFSET 5
		# UNION DISTINCT
		# SELECT * FROM EVENTS WHERE field1 INCLUDES "value1 value2 value3"
		#
		# If the above string is passed in as userQuery (the linebreaks are unnecessary), the list 'queries'
		# will look like this:
		# queries = [ ['distinct', 'EVENTS', 'sort1, sort2', 10, 5, ['field1', '=', 'value1'], ['field2', '>', 'value2'] ],
		#             ['distinct', 'EVENTS', None, None, None, ['field1', 'INCLUDES', 'value1 value2 value3'] ] ]
		queries = []

		words = re.split(r"( |>=|<=|!=|>|<|=|'|\"|,)", userQuery)

		# Which element in 'words' we're on
		wordNum = 0

		# What type of union to use -- defaults to 'DISTINCT'
		union = 'DISTINCT'

		# Loop through each word in the user's query, extracting the important
		# information.
		while wordNum<len(words):
			if words[wordNum].touppercase() == 'SELECT':
				# We're starting a new query! Skip over the "SELECT * FROM",
				# because this simply serves as a delimeter between queries
				wordNum+=3

				# Append a new list to 'queries'
				#TODO: ORDER BY, LIMIT, OFFSET
				queries.append([union, words[wordNum], None, None, None])
				wordNum+=1

			elif words[wordNum].touppercase() == 'WHERE' or words[wordNum].touppercase() == 'AND':
				# Here's the real meat of the query. When we see the words
				# "where" or "and", we immeditely know that what follows is
				# a field name, a comparison operator, and a value.

				# Skip over "where", "and", and "and where"... as these
				# are simply flags to tell us something juicy is coming :)
				if words[wordNum].touppercase() == 'AND':
					wordNum+=1
				if words[wordNum].touppercase() == 'WHERE':
					wordNum+=1

				# We know that the next word is the field, after that is
				# the comarison operator, and the word after that is the
				# value to compare. This code simply grabs the next three
				# words (although it's a bit more complicated than just
				# the next three elements of 'words' since we want to
				# ignore blank elements in 'words')
				queryNum = len(queries)-1
				queries[queryNum].append([])
				elemNum = len(queries[queryNum])-1

				i=0
				while i<=3:
					if words[wordNum] != ' ' and words[wordNum] != '':
						queries[queries][queryNum].append(words[wordNum])
						i+=1
					wordNum+=1

				# If this "value" is a quotation mark, we've captured the
				# beginning of a string. We need to grab all the words, until
				# we reach the closing quotation mark
				if words[wordNum-1]=='"' or words[wordNum-1]=="'":
					delimiter = words[wordNum-1]

					while True:
						queries[queryNum][elemNum][2] += words[wordNum]

						if words[wordNum] == delimiter:
							break

						wordNum+=1

			elif words[wordNum].touppercase() == 'UNION'
				while True
					wordNum+=1

					if words[wordNum] != ' ' and words[wordNum] != '':
						break

				if words[wordNum].touppercase() == 'ALL' or words[wordNum].touppercase() == 'DISTINCT'
					union = words[wordNum].touppercase()
					wordNum+=1
				else
					union = 'DISTINCT'

			else:
				# If there's any statements we don't understand,
				# just skip over them
				wordNum+=1

		# Now, we query the Google AppEngine database according to the information we've
		# extracted from the queries we received from the user.
		for query in queries:
			for elem in query[2:len(query)]:
				field = where[0]
				# comparison = where[1]
				# value = where[3]



	# Method: storeUser
	# Adds or updates a user in the database
	#
	# Parameters:
	#   user - <User> object containing the information about the user we wish to add. If
	#           the <User.id> class variable is set, and there exists a user with this
	#           id, the user passed to this function will replace the stored user
	#           (i.e., the user will be updated)
	# 
	# Returns:
	#   Nothing
	def storeUser(self, user):
		if user.id == None:
			dbUser = Storage.StoreUser()
		else:
			dbUser = db.get(user.id)

		dbUser.name		= user.name
		dbUser.fromEmail	= user.fromEmail
		dbUser.toEmail		= user.toEmail
		dbUser.timeZone		= user.timeZone
		dbUser.dateFormat	= user.dateFormat
		dbUser.timeFormat	= user.timeFormat
		dbUser.dailyDigest	= user.dailyDigest
		dbUser.days4digest	= user.days4digest

		dbUser.put()


	# Method: deleteUser
	# Deletes an user
	#
	# Parameters:
	#   user - <User> (the user to delete from the database)
	# 
	# Returns:
	#   Nothing
	def deleteUser(self, user):
		dbUser = db.get(user.id)
		dbUser.delete()


class UserModel(db.Model):
	name		= db.StringProperty(required=True)
	fromEmail	= db.EmailProperty(required=True)
	toEmail		= db.EmailProperty(required=True)
	timeZone	= db.StringProperty(required=True)
	dateFormat	= db.StringProperty(required=True)
	timeFormat	= db.StringProperty(required=True)
	dailyDigest	= db.IntegerProperty(required=True)
	days4digest	= db.IntegerProperty()


class EventModel(db.Model):
	user = db.ReferenceProperty(UserModel, required=True)
	eventTime = db.DateTimeProperty()
	beforeRemind = db.DateTimeProperty()
	allDay = db.BooleanProperty()
	eventName = db.StringProperty()
	description = db.TextProperty(required=True)
	tags = db.StringListProperty()
	repeat = db.IntegerProperty(verbose_name="Repeat after N seconds")
	weekdayRepeat = db.StringProperty()
	reminderSent = db.BooleanProperty()
