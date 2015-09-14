# Introduction #
This email will be quite low-level, but generally language agnostic, so
hopefully won't exclude anyone.

To get us up and running quickly, I have tried to avoid making too many
assumptions about the nature of our parser. However, there does seem to
be a desire for the system to be modular, and easy to extend.

With this in mind, I have would like to present some thoughts I have had
on a bare bones system which is built from the start with extension
plugins.

# Details #

## Messages are Transformed into Actions ##

Our abstract system needs to be able to take a message, and do some
actions in reaction to it. I'm going to start with a stupid little
diagram -
the first in a series of increasingly complicated ones:

```
   message -> actions 
```

## Transformations ##

Some amount of analysis of message is needed to "transform" the message
into actions. To keep things simple, and modular I was thinking of a
list of transforms:

```
   message -> transforms -> actions
```

For example, "remember Frank's telephone number: 555 12345" should
cause the "remember" action to do something.

I realised that a transform's output is really a collection of
key-value pairs which will be used to parameterize the actions. In the
example above, then the "remember" action needs a string to remember:
"Frank's telephone number: 555 12345".

```
   message -> transforms -> parameter dictionary -> actions.
```

It is within these transforms that the "parsing" takes place.

Initially, I think we could do these on simple regular expression
patterns, but later on take into account more NLP specific things -
e.g. POS tagging.

So for example, considering the transformation from a message to a cron
expression for scheduling. I've represent these as two transforms, but
they could be

  * "#weekdays" is detected
    * Existing cron expression is found.
    * If none is found, then use the
    * exact time (HH:mm) that the message is received.
    * Set the day of week to "1-5".
    * Add (for\_scheduling => true) to the dictionary.
    * Add (is\_repeated => true) to the dictionary.

  * "at (\d{1,2})\S+({1,2})" is detected
    * Existing cron expression is found. If none is found, then use the
    * exact time (HH:mm) that the message is received.
    * Set the hour and month to the groups captured in the regular expression.
    * Add (for\_scheduling => true) to the dictionary.

Between them, these two should 'parse' the expressions:

```
        @weekdays          => 45 21 * * 1-5    # 21:45 every week day. I sent this in at 21:45.
        at 18:30           => 30 18 * * *
        at 12              => 0 12 * * *
        @weekdays at 1100  => 0 11 * * 1-5
```

## Transform Pipeline ##

For the transforms to be efficiently chained together, the message just
becomes one more entry in the dictionary.

i.e.
```
        class ICommandTransform(Interface):
           def transform(ctx={}):
```
Of course, the message is not the only thing we can reason about in
these transforms. Any raw input into Sandy can be put into the top of
the system. I was thinking of:

```
        { message       : "Remind me to record Firefly each Tuesday at 22:30",
          input_medium  : "SMS",
          input_id      : "07971 123456",
        }
```

> From the input medium and id, a transform can detect the user. Once we
have a user, we can have their preferences about if/how to reply, as
well as how they usually like to be reminded.

```
        { message       : "Remind me to record Firefly each Tuesday at 22:30",
          input_medium  : "SMS",
          input_id      : "07971 123456",
          user          : {id : "jamesh", default_remind_medium : "email",  style : "flowery" },
        }
```


To complete the example, further transformation may give us:

```
        { message       : "Remind me to record Firefly each Tuesday at 22:30",
          input_medium  : "SMS",
          input_id      : "07971 123456",
          user          : {id : "jamesh", default_remind_medium : "email", style : "flowery" },
          remind_id     : FLOWERY_REMINDER,
          remind_medium : "email",
          sms           : "07971 123456",
          reply_id      : FLOWERY_REMIND_REPLY,
          reply_medium  : "SMS",
          remind_msg    : "record Firefly",
          email         : "jam...@sandysback.org",
          cron_expression: "30 22 * * 2"
          for_scheduling: "true",
          is_repeated   : "true",
        }
```

For me, the next thing to think about was: is there an ordering issue to
consider? i.e. are there some transforms that depend on others?
Intuitively, I'd say that there are.

For example, I expect that we will need to cover a use case of receiving
a message from email, and the message asking for the reminder to be sent
via SMS. In this case, the transform that detects users will need to be
run before the transform to find the cell phone number.

If we have to consider the ordering, then the transforms will have to
specify some metadata about its dependencies, and the framework run a
topological sort on first construction of the pipeline.

Before leaving transforms, I've written a tiny list of transforms,
together with the keys that they use to trigger the transform, and the
output keys they generate/modify.

Example transforms:

  * Simple Scheduling Tag Detector - `message -> cron_expression, for_scheduling, is_repeated`
  * Natural Language Detector      - `message -> natural_language`
  * Remember This detector         - `message -> fact_to_store, reply_id`
  * Remind Me detector             - `message -> remind_message, reply_id`
  * User detector                  - `input_medium, input_id -> user`

In summary, a transform pipeline takes dictionary of raw input and
incrementally builds up a dictionary of parameters for actions, or
other
transforms. Dependency ordering is built up at construction.

### Command Processor is Command Actions ###

The pipeline of transforms have given us parameters to actions.

Intuitively, I'm thinking that a message should trigger multiple
actions. E.g. Scheduler Trigger, Reminder Sender, Acknowledgement
Sender,
Fact Stasher, Action Logger

I am less convinced that there is an order dependency for actions,
though we may want to think of one a bit harder. (ok, I thought of a
horribly one, which is probably unrealistic - pipes, erm.)

```
        class ICommandAction:
            def perform(Dictionary ctx):
```

It is feasible that the action sequence will be invoked on its own: the
scheduler will need to trigger a task, and then run through the actions
that are needed. E.g. the same sequence of actions is used, but only
the
"triggered" actions are run, and not the "initial" actions. I guess
this is the rudiments of a lifecycle.

I think we can give the idea of triggers a bit more thought, but I'm
thinking of at least three triggers:

  * do the actions NOW
  * do the actions at this specified time (really an implementation of the next trigger)
  * do the actions when a certain event happens

For now, I'm only considering the setting up of those triggers.

(pseudo-code for CronSchedule)
```
        perform(Dictionary ctx):
           if (ctx['lifecycle-state'] != 'initial' or ctx['cron_expression'] == None)
                return
           # do the scheduling. 
```