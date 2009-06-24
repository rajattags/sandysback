from sandy2.common.parsing import IMicroParser, IMessageAction, Parser
from sandy2.common.scheduling import Scheduler
from sandy2.common.plugins import IPlugin

from datetime import datetime, timedelta

import parsedatetime.parsedatetime as pdt 
import parsedatetime.parsedatetime_consts as pdc 

class SchedulerPlugin(IPlugin):
    """Plugin to support scheduling messages to be parsed at a later date.
    
    Special tags #weekly, #daily, #hourly are do what they should do, although the behaviour of messages which give these tags with a datum time is undefined. 
    These frequency tags can be combined, though I am not sure of the utility (or even bug-free-ness) of this in its current implementation.

    The interplay between timezones: 
      * server in one TZ and user in another,
      * "remind at 10pm" 

    is also not thoroughly tested, and not expected to work.
    """

    
    def __init__(self, parser=None, db=None):
        self.is_followed_by = ['scheduling']
        self.parser = parser
        self.db = db
        self.properties = None
    
    def install(self, ctx):
        self.scheduler = Scheduler()
        self.properties['scheduler'] = self.scheduler
    
    def start_up(self, ctx):
        ctx.er.micro_parsers.add(TimedReminder())
        ctx.er.micro_parsers.add(FrequencyTagDetector())
        
        ctx.er.parser_actions.add(ScheduleAction(self.scheduler))

        commands = Commands()
        ctx.er.message_patterns.add('^scheduler', commands.inspect_scheduler)
        ctx.er.message_patterns.add('^(remind( me)?|r( me)?|echo|remember) (?P<reminder_text>.*)', commands.remind_me)
        
        ctx.er.template_files.add(self, 'ui/templates/scheduler_commands.txt')
        ctx.er.phrase_banks.add(self, 'ui/templates/zander_scheduler_commands.txt')
    
    def run(self):
        self.scheduler.start()
        
    def stop(self):
        self.scheduler.dispose()

class TimedReminder(IMicroParser):

    """Short description: try some dates"""
    def __init__(self):
        self.is_preceeded_by = ['incoming_message', 'tz_offset', 'message_datetime_local']
        self.is_followed_by = ['event_datetime', 'is_reminder', 'head']
        self.constants = None

    def micro_parse(self, metadata):
        
        tz_offset = metadata.get('tz_offset', 0)
        if tz_offset >= 12 and tz_offset <= -12:
            tz_offset *= 3600
            
        td = timedelta(0, tz_offset)

        datetime_local = metadata.get('message_datetime_local', datetime.utcnow())
        
        if self.constants is None:
            self.constants = pdc.Constants()
            self.constants.DOWParseStyle = +1 # if today is "Friday", "Tuesday" is this Tuesday, not last Tuesday.
            self.constants.CurrentDOWParseStyle = False # if today is Friday, "Friday" is next Friday, not today.

        dt = self.startTime(metadata['incoming_message'], sourceTime=datetime_local)
        if dt:
            # make sure we take into account the timezone, where appropriate.
            metadata['event_datetime'] = dt - td
        # reminder is set to true by the action below.
        if not metadata.has_key('is_reminder'):
            metadata['is_reminder'] = False
            
    def startTime(self, msg, sourceTime):
        calendar = pdt.Calendar(self.constants)
        (start, end, valid) = calendar.evalRanges(msg, sourceTime=sourceTime)
        
        if valid:
            # need to address the occurrence of 11-3pm being interpretted as 11pm-3pm
            return _f_dt(start, sourceTime)
        
        (start, valid) = calendar.parse(msg, sourceTime=sourceTime)
        if valid == 1:
            # date
            return _f_dt(start, sourceTime)
        elif valid == 2:
            # time
            return _f_dt(start, sourceTime)
        elif valid == 3:
            # datetime
            return _f_dt(start, sourceTime)
        
        return None



class Commands:

    def __init__(self, scheduler=None):
        self.scheduler = scheduler


    def inspect_scheduler(self, metadata):
        if metadata['input_medium'] == 'stdin':
            metadata['scheduler_string'] = self.scheduler.__str__() 
            metadata['command'] = 'schedule_command'
            
    
    def remind_me(self, metadata):    
        """remind, r <something> <time>:- I'll remind you of <something> at a specific time. 
                e.g. remind me to pack my SICP book 8am tomorrow.
                e.g. remind me to move the car in 10 minutes
        """
        metadata['command'] = 'remind_me_command'
        metadata['reminder_text'] = metadata['reminder_text']

            
class FrequencyTagDetector(IMicroParser):
    
    def __init__(self):
        self.is_preceeded_by = ['tags', 'special_tags']
        self.is_followed_by = ['frequency_timedelta']
        
    def micro_parse(self, metadata):
        special = metadata['special_tags']
        tags = metadata['tags']
        frequency = set()
        metadata['frequency_timedelta'] = frequency
        fmap = {
               # TODO monthly, annually
               'weekly': timedelta(7), 
               'daily': timedelta(1), 
               'hourly': timedelta(0, 3600),
               'tick': timedelta(0, 60),
               'tock': timedelta(0, 10)
               }
#        
        for tag in tags:
            td = fmap.get(tag, None)
            if td:
                tags.remove(tag)
                special.append(tag)
                frequency.add(td)
        

def _dt(start):
    return datetime(*start[0:6])

def _f_dt(time_tuple, datum):
    dt = _dt(time_tuple)
    return dt if dt > datum else dt + timedelta(1)

class ScheduleAction(IMessageAction):
    
    def __init__(self, scheduler=Scheduler(), parser=None):
        # need a database job_store here..
        self.scheduler = scheduler
        scheduler.callable = self.resubmit_jobs
        self.parser = None

        
    def perform_action(self, metadata):
        if not metadata['is_reminder']:
            # first time round, we schedule a new event.
            dt = metadata.get('event_datetime', None)
            if dt:
                self.__schedule(dt, metadata)
        else:
            # second time round, we should schedule a new event, 
            # at the prescribed frequency.
            fset = metadata.get('frequency_timedelta', set())
            for td in fset:
                self.__schedule(td, metadata)
    
    def __schedule(self, time, metadata):
        message = metadata['incoming_message']
        medium = metadata['input_medium']
        user = metadata['user_id']
        message_id = metadata.get('message_id', -255)
        self.scheduler.schedule(time, message_id, message, medium, user)
        
    def resubmit_jobs(self, message_id, message, medium, user_id):
        metadata = {"incoming_message" : message, 'is_reminder': True, "input_medium": medium, "user_id": user_id, 'message_id': message_id}
        self.parser.parse(metadata)
        self.parser.perform_actions(metadata)