#A list of pages for the web interface, along with notes on how they should be focused.

All pages assume no Ajax. We can add in Ajax, but we should make sure it also works without javascript first and then add Ajaxed pages in.



# Home Page #
Intro copy and sign in form.



# How It Works #



# How To Talk To Sandy #
Documentation showing how to construct phrases and access features (tagging, repeating events, etc.)



# Register #



# Sign In Form #
Partial template. Can occur in several places. Form to sign in w/ link to recover password. Posts sign in credentials to Dashboard page.



# Recover Password #



# Dashboard #
Requires sign in. Lists notes tied to a date plus non-dated to-dos.

User can filter for different time periods: today, yesterday, tomorrow, this week, next/prev week, this month, next/prev month, or a specific day, month, or year.



# Inbox #
Requires sign in. If not signed in, user sees sign in form.

Displays all items tagged with "inbox" sorted by oldest to newest (by default). (Items can be tagged"inbox" by users or by the system when there's a parse failure.)




# Tag Archive #
Displays all items tagged with "X".



# Type Archive #
Displays all notes of a type. (Notes, to-dos, contacts, whatever)



# Received Items #
Displays all notes received (via email, web, sms, whatever) for a given time period: today, yesterday, this week,prev week, this month, prev month, or a specific day, month, or year.



# Settings #
Requires sign in. Allows users to edit settings.



# Help #
Answer to common problems.