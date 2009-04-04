from sandy2.common.parsing import IMicroParser, IMessageAction, Parser
from sandy2.common.scheduling import Scheduler
from sandy2.common.plugins import IPlugin

from datetime import datetime, timedelta

import parsedatetime.parsedatetime as pdt 
import parsedatetime.parsedatetime_consts as pdc 

from datetime import datetime, timedelta

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
    
    def install(self):
        self.scheduler = Scheduler()
        self.properties['scheduler'] = self.scheduler
    
    def start_up(self):
        self.parser.add_micro_parser(TimedReminder())
        self.parser.add_micro_parser(FrequencyTagDetector())
        schedule_action = ScheduleAction(scheduler=self.scheduler)
        self.parser.add_action(schedule_action)
        self.parser.add_micro_parser(SchedulerInspectionCommand(schedule_action.scheduler))
    
    def run(self):
        self.scheduler.start()

class TimedReminder(IMicroParser):

    """Short description: try some dates"""
    def __init__(self):
        self.is_preceeded_by = ['incoming_message', 'tz_offset', 'message_datetime_local']
        self.is_followed_by = ['event_datetime', 'is_reminder', 'head']
        self.constants = None

    def micro_parse(self, metadata):
        
        tz_offset = metadata.get('tz_offset', 0)
        td = timedelta(0, 3600 * tz_offset)

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
            
    def startTime(self, msg, sourceTime=None):
        calendar = pdt.Calendar(self.constants)
        (start, end, valid) = calendar.evalRanges(msg, sourceTime=sourceTime)
        
        if valid:
            return _dt(start)
        
        (start, valid) = calendar.parse(msg, sourceTime=sourceTime)
        if valid == 1:
            # date
            return _dt(start)
        elif valid == 2:
            # time
            return _dt(start)
        elif valid == 3:
            # datetime
            return _dt(start)
        
        return None

class SchedulerInspectionCommand(IMicroParser):
    """Short description: Display the state of the schedule
    """
    def __init__(self, scheduler=None):
        self.is_preceeded_by = ['first_word']
        self.is_followed_by = ['reply_message', 'reminder_message']
        self.scheduler = scheduler


    def micro_parse(self, metadata):
        if metadata['first_word'] == 'schedule':
            s = self.scheduler.__str__()
            metadata['reply_message'] = s
            metadata['reminder_message'] = s
            
            
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