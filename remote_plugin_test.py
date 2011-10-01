from twisted.internet.protocol import ClientFactory
from twisted.internet import ssl
from twisted.internet import reactor
from twisted.python import log

from janecore.ircbot.ansible.protocol import AnsibleClientProtocol
from janecore.ircbot.ansible import commands
import re
import pickle

class DittoRemote(AnsibleClientProtocol):
    EVENTS=["ircPrivmsg",] #"privMsg", "queryMsg"]

    def ircPrivmsgCallback(self, data):
        print data
        if re.match("Jane.*ping?",data[-1]):
            new_data = [data[1], "pong!!!!"]
            self.callRemote(commands.DispatchEvent, event_name="ircDoMsg", data=pickle.dumps(new_data))

        if re.match(".load attention", data[-1]):
            new_data = [data[1], ".unload attention"]
            self.callRemote(commands.DispatchEvent, event_name="ircDoMsg", data=pickle.dumps(new_data))

class AnsibleClientFactory(ClientFactory):
    protocol = DittoRemote
    
factory = AnsibleClientFactory()
reactor.connectSSL("localhost", 1677, factory, ssl.ClientContextFactory())
reactor.run()
