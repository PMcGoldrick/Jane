from twisted.internet import defer, reactor
from twisted.plugin import getPlugins
from twisted.python import log
import copy
import janecore.events as events
from interface import IEventList, IEventListener, IRespondingEventList, IEventResponder
__all__=["events"]
events_lst = ["shutDown"]
responding_events = []

class EventManager(object):
    def __init__(self, owner):
        self.event_registry = {}
        self.event_types = {}
        self.owner=owner  # FIXME: oh how I love passing
                          # references around...
        self._init_faf_events()
        self._init_resp_events()
        log.msg(self.event_registry)

    def _init_resp_events(self):
        full_lst = responding_events + [
            evname for elst in getPlugins(IRespondingEventList, 
                                events) for evname in elst
            ]

        for klass_name in  full_lst:
            self.registerEventFromName(klass_name, RespondingEvt)
        
        for event_handler in getPlugins(IEventResponder):
            if not isinstance(event_handler.__class__.RESPEVENT, list):
                self.addResponder(event_handler.__class__.RESPEVENT, event_handler.respond)
            else:
                for event_name in event_handler.__class__.RESPEVENT:
                    self.addResponder(event_name, event_handler.respond)

    
    def _init_faf_events(self):
        """
        Generate classes and initializes listeners for 'system events'.
        Please use global registration as last resort.
        """
        for klass_name in events_lst + [evname for elst in getPlugins(IEventList, events) for evname in elst]:
            self.registerEventFromName(klass_name, Evt)
        # Register Listeners
        for event_handler in getPlugins(IEventListener, events):
            if not isinstance(event_handler.__class__.EVENT, list):
                self.addListener(event_handler.__class__.EVENT, event_handler)
            else:
                for event_name in event_handler.__class__.EVENT:
                    self.addListener(event_name, event_handler)
        
    def getEventByName(self, event_name, data, maintain_original=False, callback_deferred=None):
        """ 
        dynamically create and event object from the classes registered with the event manager
        OR DIE
        """
        try:
            if callback_deferred: 
                evt = self.event_types[event_name](data, callback_deferred)
            else:
                evt = self.event_types[event_name](data, maintain_original)

        except KeyError:
            log.msg("Event is not registered: %s" % event_name)
            return
        except TypeError:
            log.msg("Attempted to pass deferred to a FaF event constructor")
            return
        else:
            return evt

    def dispatch(self, event_name, data, maintain_original=False, callback_deferred=None):
        """ dispatch this event to the correct dispatcher """
        evt = self.getEventByName(event_name, data, maintain_original, callback_deferred)
        if not evt: 
            return
        elif isinstance(evt, RespondingEvt):
            self._dispatchRespondingEvent(evt)
        elif isinstance(evt, Evt):
            self._dispatchFaFEvent(evt)

    def _dispatchFaFEvent(self, event):
        """ Dispatch a Fire and Forget event (Evt) """
        ## Handle Normal Events
        l = []
        log.msg("\n### DISPATCHING ### \n %s \n %s" % (event.value, event.data))
        if event.value in self.event_registry.keys() \
        and len(self.event_registry[event.value]) > 0:
            for f in self.event_registry[event.value]:
                l.append(defer.maybeDeferred(f, event))
        else:
            l.append(defer.succeed(event.data))

        return defer.DeferredList(l, consumeErrors=False).addErrback(self.errBack)

    def _dispatchRespondingEvent(self,evt):
        """ Dispatch an event that responds through Deferrred.callback """
        evt.respond(self.event_registry[evt.value][0])

    def register(self, eventclass):
        """ Register a new Event """
        log.msg("registering event %s " % eventclass.EVENT)
        if self.event_registry.has_key(eventclass.EVENT):
            raise(AttributeError(
                "Event already registered: %s" % eventclass.EVENT))
        else:
            self.event_registry[eventclass.EVENT] = []
    
    def registerEventFromName(self, klass_name, base_klass):
        """ 
        Helper to automatically create an event class
        from an event name.
        """
        klass = type(klass_name[0].capitalize() + klass_name[1:], (base_klass,), 
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
            else:
                return 
    
    def addResponder(self, eventvalue, responder):
        """ Callback must be callable """
        if not callable(responder):
                responder = getattr(responder, eventvalue+"Responder"
                    ) if hasattr(responder, eventvalue+"Responder"
                    ) else getattr(responder, "respond")
        
        if self.event_registry.has_key(eventvalue) and \
                len(self.event_registry[eventvalue]) == 0:
            
            log.msg("#### Adding responder for %s" % eventvalue)
            self.event_registry[eventvalue].append(responder)
        else:
            raise(AttributeError("Event not registered maybe...%s" % eventvalue))

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

class RespondingEvt(object):
    """ 
    Exclusive event that responds only to the caller via calling back the deferred
    """
    def __init__(self, data, callback_deferred):
        self.data = data
        self.value = self.__class__.EVENT
        self._cb = callback_deferred

    def respond(self, responder):
        """ 
        """
        # Let the stack unwind
        reactor.callLater(0,responder, self._cb)


