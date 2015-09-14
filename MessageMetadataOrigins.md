reminder\_db\_plugin.py:class DigestMicroParser(IMicroParser):
  * first\_word (w):
  * reminder\_message (w):
  * reply\_message (w):
  * user\_id (r):

gmail\_plugin.py:class EmailUserFinder(IMicroParser):
  * email\_id (w):
  * email\_id (r):
  * email\_subject (w):
  * incoming\_message (r):
  * input\_medium (r):
  * user\_id (r):
  * user\_id (r):
  * user\_id (w):

gmail\_plugin.py:class EmailUserCreator(IMicroParser):
  * email\_id (r):
  * input\_medium (w):
  * user\_id (r):

console\_plugin.py:class ExitCommand(IMicroParser):
  * input\_medium (w):
  * STOP (w):

console\_plugin.py:class ConsoleUserFinder(IMicroParser):
  * console\_id (w):
  * fullname (w):
  * user\_id (w):

console\_plugin.py:class ConsoleOutputReply(IMessageAction):
  * output\_medium (r):
  * output\_message (r):

base\_plugin.py:class TokenizerParser(IMicroParser):
  * first\_word (w):
  * incoming\_message (r):
  * STOP (w):
  * tokens (w):

base\_plugin.py:class TagExtractor(IMicroParser):
  * tags (w):
  * tokens (r):
  * special\_tags (w):

base\_plugin.py:class OutputSelector(IMicroParser):
  * input\_medium (r):
  * output\_message (w):
  * output\_medium (w):
  * output\_message (w):
  * output\_medium (w):
  * output\_message (w):
  * output\_medium (w):
  * output\_medium (w):
  * output\_message (w):
  * output\_message (w):
  * special\_tags (r):
  * tags (r):
  * tags (w):

transports/mailer.py:class MailParser(object):
  * email\_id (w):
  * email\_in\_reply\_to (w):
  * email\_id (r):
  * email\_message\_id (w):
  * email\_my\_address (w):
  * email\_recipients (w):
  * email\_subject (r):
  * email\_subject (w):
  * fullname (w):
  * fullname (r):,
  * input\_medium (w):
  * incoming\_message (w):
  * message\_datetime\_local (w):
  * tz\_offset (w):

message\_db\_plugin.py:class MessageRecorder(IMicroParser):
  * input\_medium (r):
  * incoming\_message (r):
  * is\_reminder (r):
  * message\_id (w):
  * user\_id (r):

introspection\_plugin.py:class InspectCommand(IMicroParser):
  * first\_word (r):
  * reminder\_message (w):
  * reply\_message (w):
  * tokens (r):
  * tokens (r):[1](1.md)

introspection\_plugin.py:class MetadataCommand(IMicroParser):
  * first\_word (r):
  * output\_message (w):
  * reminder\_message (w):
  * reply\_message (w):

introspection\_plugin.py:class HelpCommand(IMicroParser):
  * first\_word (r):
  * reminder\_message (w):
  * reply\_message (w):

introspection\_plugin.py:class TimeCommand(IMicroParser):
  * first\_word (r):
  * reminder\_message (w):
  * reply\_message (w):

introspection\_plugin.py:class EchoCommand(IMicroParser):
  * first\_word (r):
  * reminder\_message (w):
  * reply\_message (w):

reminder\_plugin.py:class TimedReminder(IMicroParser):
  * event\_datetime (w):
  * incoming\_message (r):
  * is\_reminder (w):

reminder\_plugin.py:class SchedulerInspectionCommand(IMicroParser):
  * first\_word (w):
  * reminder\_message (w):
  * reply\_message (w):

reminder\_plugin.py:class FrequencyTagDetector(IMicroParser):
  * frequency\_timedelta (w):
  * special\_tags (r):
  * tags (r):

reminder\_plugin.py:class ScheduleAction(IMessageAction):
  * incoming\_message (r):
  * input\_medium (r):
  * is\_reminder (r):
  * user\_id (r):

database\_plugin.py:class NewUserCreator(IMicroParser):
  * create\_new\_user (w):
  * create\_new\_user (w):
  * fullname (r):
  * fullname (r):
  * fullname (w):
  * input\_medium (r):
  * input\_medium (r):
  * reminder\_medium (w):
  * tz\_offset (r):
  * tz\_offset (r):
  * tz\_offset (r):
  * tz\_offset (r):
  * tz\_offset (w):
  * user\_id (w):