from twisted.internet import protocol, reactor
from twisted.python import log
from twisted.plugin import getPlugins 

from janecore.ircbot.client import JaneIRCClient
from janecore.eventmanager import EventManager
from janecore.eventmanager.interface import IEventListener
from janecore import common, plugins

class JaneIRCClientFactory(protocol.ClientFactory):
    """ 
    IRC Client factory. There should only ever be one of these
    so it's OK to instantiate storage here
    """
    protocol = JaneIRCClient

    def __init__(self, realname=None, nickname=None, password=None, 
                 channels_dict={}):
        self.initial_channels = channels_dict
        self.realname = realname
        self.username = realname
        self.nickname = nickname
        self.password = password
        # Allow the callstack to unwind before firing up
        # more boilerplate stuff. 
    
    def startFactory(self):
        self.storage = common.Storage("core")
        self.storage.evt_mgr = EventManager(self)
        self.storage.evt_mgr.addListener("connectionLost", 
                self.connectionLostCallback)
        self.storage.ircClientFactory = self
    
    def buildProtocol(self, addr):
        p = self.protocol()
        p.factory = self
        for event_name in self.protocol.EVENT:
            self.storage.evt_mgr.addListener(event_name, p)

        for handler in getPlugins(IEventListener, plugins):
            handler.load(self)
            for event_name in handler.EVENT:
                self.storage.evt_mgr.addListener(event_name, handler)
        return p

    def clientConnectionLost(self, connector, reason):
        log.msg("Lost connection (%s), reconnecting." % (reason,))
        self.storage.evt_mgr.dispatch("connectionLost", [connector, reason])
    
    def connectionLostCallback(self, evt):
        """ Callback Example """
        connector, reason = evt.data
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        log.msg("Could not connect: %s" % (reason,))
