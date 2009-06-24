from sandy2.common import NOP

"""Module to add the concept of extensions and extension points.

Extension points are an encapsulation technique hiding the implementation 
details of an extensible subsystem from a contributing plugin. 

This removes the need to expose much of the implementation to the plugin framework, 
and simplifies a plugins interactions with the rest of the framework."""
    
class ExtensionRegistry:
    """Clients are unlikely need to be able to instantiate this object."""
    
    def __init__(self, configure=NOP):
        if configure is not None and callable(configure):
            self._configure = configure
        self._extension_points = {}
        
    def __getattr__(self, extension_point_name):
        return self._extension_points.setdefault(extension_point_name, ExtensionPoint(self._configure))

class ExtensionPoint:
    
    def __init__(self, configure):
        self._extensions = []
        self._addition_trackers = []
        self._removal_trackers = []
        self._configure = configure
        pass
    
    def add(self, obj, *args, **kw):
        for tracker in self._addition_trackers:
            tracker(obj, *args, **kw)
        
        self._configure(obj)
        # not sure if this is completely horrible or not.
        for o in args:
            self._configure(o)
        self._extensions.append((obj, args, kw))
        
    def remove(self, obj):
        self._extensions = filter(lambda t : t[0] is obj, self._extensions)
        for tracker in self._removal_trackers:
            tracker(obj)
            
    def track(self, tracker):
        has_methods = False
        
        adder = getattr(tracker, "register", None)
        if adder and callable(adder):
            self._track_additions(adder)
            has_methods = True

        remover = getattr(tracker, "unregister", None)
        if remover and callable(remover):
            self._track_removals(remover)
            has_methods = True
             
        if not has_methods and callable(tracker):
            self._track_additions(tracker)
        
    def _track_additions(self, tracker):
        self._addition_trackers.append(tracker)
        
        for (obj, args, kw) in self._extensions:
            tracker(obj, *args, **kw)
        
    def _track_removals(self, tracker):
        self._removal_trackers.append(tracker)
        
    def untrack(self, tracker):
        has_methods = False
        
        adder = getattr(tracker, "register", None)
        if adder and callable(adder):
            del self._addition_trackers[adder]
            has_methods = True
        remover = getattr(tracker, "unregister", None)
        if remover and callable(remover):
            del self._track_removals[remover]
            has_methods = True
             
        if not has_methods and callable(tracker):
            del self._addition_trackers[tracker]

    def __iter__(self):
        return self._extensions.__iter__()

class IExtensionTracker:
    
    def __init__(self):
        pass
    
    def register(self, obj):
        pass
    
    def unregister(self, obj):
        pass