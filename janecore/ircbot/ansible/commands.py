from twisted.protocols import amp

class DispatchEvent(amp.Command):
    arguments = [('event_name', amp.String()),
               ('data', amp.String())]
    response = []

class RegisterListener(amp.Command):
    arguments = [('event_name', amp.String())]
    response = []

class AuthenticatePlugin(amp.Command):
    arguments = [("username", amp.String()),
                 ("pass", amp.String())]
    response = []

class EventFired(amp.Command):
    """ 
    Received by client when an event he has
    registered as a listener to has fired
    """
    arguments = [("event_name", amp.String()),
                 ("data", amp.String())]
    response = []

