This is a very early commit. 

It is *not* intended as a release to users, but a proof of a number of concepts:

 * modular design
 * message handler a.k.a. parser built up of many message/metadata transforms a.k.a. micro-parsers.
 * scheduler
 * date parsing via parsedatetime. 

There is a rudimentary console, which should act like a command line. This is the only interface at the moment. 

The architecture is such that the system starts all threads it needs (e.g. poll for input, poll for email etc), so it needs to be thought 
about how a web server comes into the picture. 

There are very few commands. inspect, time, schedule, help and echo all do approximately what you think they might, but not really. 
They are all provided by the introspection_plugin.py.

TODO
A useful datastore is the most pressing thing atm. Considering CouchDB, though something that scales down would be better further would be better.
It is intended that you should be able to write new message media adapters (e.g. email, twitter) easily, 
and orthogonally to adding new commands. 
It is intended that a valid message through a given medium should suffice to introduce a new user to the system.
Tying multiple media together e.g. telling the system that this twitter account is me, who owns this email address, needs to be thought about.

Dependencies:
 * parsedatetime
 * sqllite3