from zope.interface import Interface, Attribute

class IEventList(Interface):
    """ Class for holding event names """

class IRespondingEventList(Interface):
    """ Class for holding responding events """

class IEventListener(Interface):
    EVENT = Attribute("""
    @type list: A list of strings representing the event(s) that this listener listens to 
    """)
    
    def callback(event): #@NoSelf
        """ 
        fallback method called when the event is triggered,
        @return: event
        @attention: Implementors MUST return the event (molested or otherwise)
        if the event is not returned the event callback chain will break. 
        """

class IEventResponder(Interface):
    """ Class for responding to RespondingEvents """
    EVENT = Attribute("""
    @type list: A list of strings representing the RespondingEvent(s) that this
    listens for and responds to """)

    def respond(event):
        """
        respond to a ResponseEvent
        """
