
from threading import Timer, Lock


from datetime import datetime, timedelta


    
def _nop(*args, **kw):
    return args

class Scheduler(object):
    """Schedule calls to the same callable, but with different parameters. 
    
    The idea is to make sure that this object is very low memory footprint, 
    and run with very few threads. 
    
    If the callable wishes to use extra threads, then this is up to it, not this scheduler.
    
    Storing of the parameters for the callable uses an external object. The so-called "job-store" is passed in at construction time. 
    By default, a naive and very inefficient in memory all-dictionary is provided if none is given.
    
        def run_my_job(self, id, username, message):
            print "id=%s user=%s message=%s" % (id, username, message)
    
        scheduler = Scheduler(self.run_my_job)
    
        tomorrow = datetime.datetime + datetime.timedelta(1, 0)

        scheduler.schedule(tomorrow, "id", "me", "wake me up")
    """
    
    def __init__(self, function=_nop, job_store=None):
        """The callable to be parameterized, and the job store. If no job store is provided, then an InMemoryJobStore is used.
        Any scheduled jobs in the job store will be re-scheduled. If there are any jobs in the job store which have not been run yet, 
        but were scheduled to run before we were started, this will run those jobs immediately. 
        """
        self.db = None
        self.current_job_timer = None
        self.current_job_seconds_abs = _dt_to_s(datetime.max)
        self.callable = function
        self.job_store = job_store if job_store else InMemoryJobStore()
        
        self.lock = Lock()
        # make sure we don't have any more jobs waiting
        self.start()

    def start(self):
        self.is_disposed = False
        if hasattr(self.job_store, 'start') and callable(self.job_store.start):
            self.job_store.start()
        return self.__reschedule()


    def __manage_timer(self, seconds_abs):
        if seconds_abs is None:
            self.current_job_timer = None
            self.current_job_seconds_abs = _dt_to_s(datetime.max)
            return
       
        now_seconds_abs = _dt_to_s(datetime.utcnow())
        if self.current_job_seconds_abs > seconds_abs or now_seconds_abs > self.current_job_seconds_abs:
            if self.current_job_timer is not None:
                self.current_job_timer.cancel()
            
            seconds_rel = seconds_abs - now_seconds_abs
            if seconds_rel < 0:
                seconds_rel = 0
            self.current_job_timer = Timer(seconds_rel, self.__process_jobs)
            self.current_job_seconds_abs = seconds_abs
            self.current_job_timer.start()
    
    def schedule(self, time_obj, *job_kw, **job_kwargs):
        """Schedule the callable with the given parameters. The time object can be a datetime, a timedelta (relative to now) or an int/float.
        The latter case is interpretted as seconds from now. 
        """
        job_dt = _to_dt(time_obj)
        
        seconds_abs = _dt_to_s(job_dt)
        
        try:
            self.lock.acquire()
            if self.is_disposed:
                raise SchedulerDisposedException()        
            self.job_store.store_job(seconds_abs, *job_kw, **job_kwargs)
            self.__manage_timer(seconds_abs)
        finally: 
            self.lock.release()

    def __str__(self):
        return "Next scheduled job is for: %s.\n%s" % (_s_to_dt(self.current_job_seconds_abs), str(self.job_store))

    def __process_jobs(self):
        # do two things in this method:
        # actually deal with the jobs that are scheduled, 
        try:
            self.lock.acquire()
            
            if self.is_disposed:
                return

            # but first we must
            self.__reschedule()
            
            # collect all the jobs to do now.
            ready_jobs = self.job_store.find_ready_jobs(_dt_to_s(datetime.utcnow()))
            
            # TODO what happens if someone pulls the plug, now??
            
            for job_kw in ready_jobs:
                try:
                    self.callable(*job_kw[1], **job_kw[2])
                except Exception, e:
                    # shouldn't crash the scheduler
                    print e
                    pass
        # if speed is really important to us, then we should consider farming the jobs 
        # off to other threads.
        finally:
            self.lock.release()
        
            
    def __reschedule(self):
        if not self.is_disposed:
            seconds_abs = self.job_store.find_next_earliest_time()
            self.__manage_timer(seconds_abs)
    
    def dispose(self):
        """Dispose of this scheduler, and stop waiting for any scheduled jobs
        """
        try:
            self.lock.acquire()
            self.is_disposed = True
            if self.current_job_timer is not None:
                self.current_job_timer.cancel()
                self.current_job_timer = None
        finally:
            self.lock.release()
            

def _to_dt(time_obj):
    t = type(time_obj)
    if t is datetime:
        return time_obj
    if t is int or t is float:
        # back in 10 == back in 10 seconds
        time_obj = timedelta(0, time_obj)
        t = type(time_obj)            
    if t is timedelta:
        return datetime.utcnow() + time_obj

def _dt_to_s(dt):
    return _td_to_s(dt - datetime.min)

def _s_to_dt(s):
    return str(datetime.min + timedelta(0, s)) if s <= 9000 * 365 * 24 * 3600 else "never"


def _td_to_s(td):
    total = td.days * 24 * 3600
    # total now in seconds
    total += td.seconds
    total += td.microseconds / 1e6
    
    return total
    
def _t_to_td(t):
    return datetime.today() + t


class IJobStore(object):
    
    def __init__(self):
        pass
    
    def store_job(self, abs_seconds, *job_kw, **job_kwargs):
        pass
    
    def find_ready_jobs(self, now):
        pass
    
    def find_next_earliest_time(self):
        return _dt_to_s(datetime.max)

class InMemoryJobStore(IJobStore):
    def __init__(self):
        self.jobs = list()
        
    def store_job(self, job_time, *job_kw, **job_kwargs):
        self.jobs.append((job_time, job_kw, job_kwargs))
        
    def find_ready_jobs(self, now):
        ready_jobs = filter(lambda job : now >= job[0], self.jobs)
        self.jobs = filter(lambda job : now < job[0], self.jobs)
        return ready_jobs
            
    def find_next_earliest_time(self):
        max = _dt_to_s(datetime.max)
        min = max
        for job in self.jobs:
            if min > job[0]:
                min = job[0]
                

        if max == min:
            return None
        else:
            return min

    def __str__(self):
        return "\n->".join(map(lambda t: str(_s_to_dt(t[0])), self.jobs))

class SchedulerDisposedException(Exception):
    def __init__(self):
        pass