# Class: Email
# Provides easy access to headers of an email

class Email:
	### Public Variables ###

	# Variable: toEmail
	# *string:* (public) Addresse(s) of the email
	toEmail = '';

	# Variable: fromEmail
	# *string:* (public) Email address of the sender
	fromEmail = '';

	# Variable: message
	# *string:* (public) The body of the email, except part that has been quoted (such as in a forward or reply)
	message = '';

	# Variable: quote
	# *string:* (public) Quoted text (if this email is a forward or reply)
	quote = '';


	### Private Variables ###

	# None


	### Public Methods ###

	# Method: __init__
	# Sets the public variables to what this method can parse from *email*.
	# Sets variable(s) to None if that part of the email is not present.
	#
	# Parameters:
	#   email - (string) raw email

	def __init__(self, email):

	
	### Private Methods ###

	# None
