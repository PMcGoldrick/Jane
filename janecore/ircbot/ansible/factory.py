from twisted.internet import protocol, reactor
from protocol import AnsibleProtocol
from janecore.common import Storage

class AnsibleFactory(protocol.Factory):
    protocol = AnsibleProtocol
    max_connections = 100
    def __init__(self):
        self.init_deferred = None
        self.storage = None
        self.number_of_connections = 0 
        
    def _setIrcClientFactory(self):
        print "attempting to set ircclientfactory"
        print self.storage
        try:
            self.evt_mgr = self.storage.evt_mgr
        except AttributeError:
            reactor.callLater(0.1, self._setIrcClientFactory)

    def startFactory(self):
        print "start factory called" 
        if not self.storage:
            self.storage = Storage("core")
        self._setIrcClientFactory()

    def buildProtocol(self, addr):
        p = self.protocol()
        p.factory = self
        return p
