""" 
Note that not all of these events are consumed
or implemented
"""
from zope.interface import implements
from twisted.plugin import IPlugin
from ..eventmanager import IEventList

class IRCEventList(list):
    implements(IPlugin, IEventList)


# Things we see other people do
observed_events = IRCEventList(["userJoined", "userLeft", "userQuit", 
                                "userKicked", "modeChanged", "noticed", 
                                "userRenamed",])

# Things the server does or we do with the server
system_events = IRCEventList(["onSignedOn", "listStarted", "listEnded", 
                              "receivedlist", "receivedMOTD",])

# Things that happen to us
action_events = IRCEventList(["joined", "left", "kicked","nickChanged",
                              "privMsg", "queryMsg", "msg",])

# Application specific events
core_events = IRCEventList(["factoryStarted", "protocolCreated", 
                            "connectionLost", "connectionMade"])

# Events actionable by us.
incoming_events = IRCEventList(["doSay","doJoin", "doPart", "doKick", 
                                "doAway", "doBack", "doNick", "doList",])
