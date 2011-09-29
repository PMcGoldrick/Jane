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

name = ""
password = ""
irc_host = ""
irc_port = 
default_channel = ""
ansible_port = 
sslkey = ""
sslcert= ""



parent_service = service.MultiService()

# TODO: add service controls via janecore.service
#jane_service = JaneIRCService()
#jane_service.setServiceParent(parent_service)
factory = JaneIRCClientFactory(name, password, default_channel)
ssl_context_factory = ssl.ClientContextFactory()
irc_client_service = internet.SSLClient(irc_host, irc_port, factory, 
        ssl_context_factory)
irc_client_service.setServiceParent(parent_service)
application = service.Application("Jane")
parent_service.setServiceParent(application)

#ansible_service = AnsibileService()
#ansible_service = setServiceParent(parent_service)
ansible_factory = AnsibleFactory()
ctx = ssl.DefaultOpenSSLContextFactory(sslkey, sslcert)
ansible_service = internet.SSLServer(ansible_port, ansible_factory, ctx)
ansible_service.setServiceParent(parent_service)
