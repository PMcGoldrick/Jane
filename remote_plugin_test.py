from twisted.internet.protocol import ClientFactory
from twisted.internet import reactor
from twisted.python import log

from janecore.ircbot.ansible.protocol import AnsibleClientProtocol
from janecore.ircbot.ansible import commands

import pickle

class DittoRemote(AnsibleClientProtocol):
    EVENTS=["msg",] #"privMsg", "queryMsg"]

    def msgCallback(self, data):
        self.callRemote(commands.DispatchEvent, event_name="doSay", data=pickle.dumps(data))
    
class AnsibleClientFactory(ClientFactory):
    protocol = DittoRemote
    
factory = AnsibleClientFactory()
reactor.connectTCP("localhost", 1677, factory)
reactor.run()
