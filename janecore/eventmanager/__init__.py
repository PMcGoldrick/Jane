from twisted.internet import defer
from twisted.plugin import getPlugins
from twisted.python import log
import copy
import janecore.events as events
from interface import IEventList, IEventListener
__all__=["events"]
events_list = ["shutDown"]

class EventManager(object):
    def __init__(self, owner):
        self.event_registry = {}
        self.event_types = {}
        self.owner=owner  # FIXME: oh how I love passing
                          # references around...
        # Generate classes for 'system events'
        # please use global registration as last resort.
        for klass_name in events_list + [evname for elist in getPlugins(IEventList, events) for evname in elist]:
            self.registerEventFromName(klass_name)
        # Register Listeners
        for event_handler in getPlugins(IEventListener):
            if not event_handler.__class__.EVENT.__class__ == list:
                self.addListener(event_handler.__class__.EVENT, event_handler)
            else:
                for event_name in event_handler.__class__.EVENT:
                    self.addListener(event_name, event_handler)
        log.msg(self.event_registry)

    def dispatch(self, event_name, data, maintain_original=False):
        """ Dispatch the event by deferreds """
        l = []
        # TODO: catch attempts to dispatch unregistered events
        event = self.event_types[event_name](data, maintain_original)
        if event.value in self.event_registry.keys() \
        and len(self.event_registry[event.value]) > 0:
            for f in self.event_registry[event.value]:
                l.append(defer.maybeDeferred(f, event))
        else:
            l.append(defer.succeed(data))

        return defer.DeferredList(l, consumeErrors=True).addErrback(self.errBack)
                    
    def register(self, eventclass):
        """ Register a new Event """
        log.msg("registering event %s " % eventclass.EVENT)
        if self.event_registry.has_key(eventclass.EVENT):
            raise(AttributeError(
                "Event already registered: %s" % eventclass.EVENT))
        else:
            self.event_registry[eventclass.EVENT] = []
    
    def registerEventFromName(self, klass_name):
        """ 
        Helper to automatically create an event class
        from an event name.
        """
        klass = type(klass_name[0].capitalize() + klass_name[1:], (Evt,), 
                    {'EVENT' : klass_name})
        self.event_types[klass_name] = klass
        self.register(klass)
        
    def addListener(self, eventvalue, callback):
        """ Register a callback for an event """
        log.msg("registering callback for %s" % eventvalue)
        
        # Attempt to discover the callback method
        # TODO: this is a bit messy, clean it up a bit.
        if not callable(callback):
            callback = getattr(callback, eventvalue+"Callback"
                    ) if hasattr(callback, eventvalue+"Callback"
                    ) else getattr(callback, "callback")

        if self.event_registry.has_key(eventvalue):
            self.event_registry[eventvalue].append(callback)
        else:
            raise(AttributeError("Event not registered %s" % eventvalue))

    def removeListener(self, eventvalue, callback):
        if not hasattr(callback, "__call__"):
             callback = getattr(callback, eventvalue+"Callback"
                     ) if hasattr(callback, eventvalue+"Callback"
                     ) else getattr(callback, "callback")
        try:
            self.event_registry[eventvalue].remove(callback)
        except Exception as ex:
             log.error(ex)

    def removeListenerByValue(self, callback):
            """
            This is a helper that iterates through all events searching
            for the value provided. Slow and sucky. 
            """
            for value in self.event_registry.values():
                try:
                    value.remove(callback)
                except ValueError:
                    continue

    def errBack(self, error):
        log.msg("Error handling event dispatch", error)

class Evt(object):
    def __init__(self, data, maintain_original):
        """ 
        @param data: any payload that needs to be used by the event
        handlers.
        @param maintain_original: when set to true, create and attempt
        to prevent modification of the original data passed in during
        event creation.
        """
        if maintain_original:
            self._data = copy.deepcopy(data) # Unmolested
        else:
            self._data = None
        self.data = data
        self.value = self.__class__.EVENT
        
    def original_data(self):
        """ Method to attempt to prevent the molestation of _data """
        if self._data:
            return self._data
        else:
            raise AttributeError(
                    "%s: original_data not creted" % self.__class__.__name__)

