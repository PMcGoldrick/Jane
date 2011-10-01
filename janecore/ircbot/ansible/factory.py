from twisted.internet import protocol, reactor
from twisted.python import log
from protocol import AnsibleProtocol
from janecore.common import Storage

class AnsibleFactory(protocol.Factory):
    """ 
    Factory to manage Ansible connections. Ansible
    clients are plugins run in a separate process on a local
    or remote matchine, conmunicating via Asynchronous Messaging 
    protocol
    """
    protocol = AnsibleProtocol
    max_connections = 100

    def __init__(self):
        self.storage = None
        self.number_of_connections = 0 
        
    def _setIrcClientFactory(self):
        """ 
        Get a handle on the event manager and storage
        """
        # IF the IRCClientFactory isn't started
        # call ourselves again later, until 
        # the evt_mgr is set
        try:
            self.evt_mgr = self.storage.evt_mgr
        except AttributeError:
            reactor.callLater(0.1, self._setIrcClientFactory)

    def startFactory(self):
        if not self.storage:
            self.storage = Storage("core")
        self._setIrcClientFactory()

    def buildProtocol(self, addr):
        p = self.protocol()
        p.factory = self
        return p
