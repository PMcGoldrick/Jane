"""
Run me using twistd:
$twistd -n --python server.py
"""
from twisted.internet import ssl
from twisted.application import service, internet
from janecore.ircbot.factory import JaneIRCClientFactory
from janecore.ircbot.client import JaneIRCClient
from janecore.ircbot.service import JaneIRCService, AnsibleService
from janecore.ircbot.ansible.factory import AnsibleFactory
from config import config

parent_service = service.MultiService()

# TODO: add service controls via janecore.service
#jane_service = JaneIRCService()
#jane_service.setServiceParent(parent_service)
factory = JaneIRCClientFactory(config["ircUserName"],config["ircNick"], 
          config["ircPassword"], config["ircDefaultChannels"])
if config["ircServerSSL"]:
    ssl_context_factory = ssl.ClientContextFactory()
    irc_client_service = internet.SSLClient(config["ircServer"], config["ircPort"], 
        factory, ssl_context_factory)
else:
    irc_client_server = internet.TCPClient(config["ircServer"], config["ircPort"],
                        factory)

irc_client_service.setServiceParent(parent_service)
application = service.Application("Jane")
parent_service.setServiceParent(application)

#ansible_service = AnsibileService()
#ansible_service = setServiceParent(parent_service)
if config["ansibleEnabled"] and config["ansibleSSL"]:
    ansible_factory = AnsibleFactory()
    ctx = ssl.DefaultOpenSSLContextFactory(config["ansibleSSLKey"], 
                                          config["ansibleSSLCert"])
    ansible_service = internet.SSLServer(config["ansiblePort"], ansible_factory, ctx)
    ansible_service.setServiceParent(parent_service)
elif config["ansibleEnabled"]:
    ansible_factory = AnsibleFactory()
    ansible_service = internet.TCPServer(config["ansiblePort"], ansible_factory)
    ansible_service.setServiceParent(parent_service)
