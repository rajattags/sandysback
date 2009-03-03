from sandy2.common.parsing import IMicroParser, IMessageAction, Parser
from sandy2.common.scheduling import Scheduler
from sandy2.common.plugins import IPlugin

from datetime import datetime, timedelta

import parsedatetime.parsedatetime as pdt 
import parsedatetime.parsedatetime_consts as pdc 

from datetime import datetime, timedelta

class SchedulerPlugin(IPlugin):
    """Plugin to support scheduling messages to be parsed at a later date.
    
    Special tags @weekly, @daily, @hourly are do what they should do, although the behaviour of messages which give these tags with a datum time is undefined. 
    These frequency tags can be combined, though I am not sure of the utility (or even bug-free-ness) of this in its current implementation.

    The interplay between timezones: 
      * server in one TZ and user in another,
      * "remind at 10pm" 

    is also not thoroughly tested, and not expected to work.
    """

    
    def __init__(self, parser=None, db=None):
        self.parser = parser
        self.db = db
    
    def start_up(self):
        self.parser.add_micro_parser(TimedReminder())
        self.parser.add_micro_parser(FrequencyTagDetector())
        self.parser.add_micro_parser(OutputSelector())
        schedule_action = ScheduleAction()
        self.parser.add_action(schedule_action)
        self.parser.add_micro_parser(SchedulerInspectionCommand(schedule_action.scheduler))
    

class TimedReminder(IMicroParser):

    """Short description: try some dates"""
    def __init__(self):
        self.is_preceeded_by = ['incoming_message', 'tz_offset', 'message_datetime_local']
        self.is_followed_by = ['event_datetime', 'reminder', 'head']

    def micro_parse(self, metadata):
        
        tz_offset = metadata.get('tz_offset', 0)
        td = timedelta(0, 3600 * tz_offset)

        datetime_local = metadata.get('message_datetime_local', datetime.now())
        
        dt = self.startTime(metadata['incoming_message'], sourceTime=datetime_local)
        if dt:
            # make sure we take into account the timezone, where appropriate.
            metadata['event_datetime'] = dt + td
        # reminder is set to true by the action below.
        metadata.setdefault('reminder', False)
            
    def startTime(self, msg, constants=pdc.Constants(), sourceTime=None):
        calendar = pdt.Calendar(constants)
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

class OutputSelector(IMicroParser):
    
    def __init__(self):
        self.is_preceeded_by = ['reply_message', 'reminder_message', 'reminder', 'event_datetime', 'tags', 'special_tags']
        self.is_followed_by = ['output_message', 'output_medium']
       
    def micro_parse(self, metadata):
        tags = filter(lambda x : x in ('noconfirm', 'noreminder'), metadata['tags'])
        metadata['tags'] = filter(lambda x : x in tags, metadata['tags'])
        metadata['special_tags'].extend(tags)
        
        
        metadata['output_message'] = ""
        metadata['output_medium'] = ""
        
        # check we actually have some input.
        if len(metadata.get('incoming_message', "")) == 0:
            return
        elif not metadata.get('reply_message', None):
                metadata['output_message'] = "I'm not sure what to do with your request"
                metadata['output_medium'] = metadata['reply_medium']
                return
        
        if metadata.get('reminder', None):
            # if this is a reminder, 
            if 'noreminder' not in tags:
                metadata['output_message'] = metadata['reminder_message']
                metadata['output_medium'] = metadata['reminder_medium']
        else:
            # this is a reply, and we probably need to talk back.
            metadata['output_medium'] = metadata['reply_medium']
            if metadata.get('event_datetime', None):
                # a reply to a schedule request.
                if 'noconfirm' not in tags:
                    metadata['output_message'] = "Confirm: %s (at %s)" % (metadata['incoming_message'], metadata['event_datetime'])
            else:
                metadata['output_message'] = metadata['reply_message']
                
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
    
    def __init__(self):
        # need a database job_store here..
        self.scheduler = Scheduler(self.resubmit_jobs)
        self.parser = None
        
    def resubmit_jobs(self, message, medium, user):
        metadata = {"incoming_message" : message, "reminder": True, "input_medium": medium, "user_id": user}
        self.parser.parse(metadata)
        self.parser.perform_actions(metadata)
        
    def perform_action(self, parser, metadata):
        self.parser = parser

        if not metadata['reminder']:
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
    
    def __schedule(self, t, metadata):
        message = metadata['incoming_message']
        medium = metadata['input_medium']
        user = metadata['user_id']
        self.scheduler.schedule(t, message, medium, user)