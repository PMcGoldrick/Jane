from twisted.internet.protocol import ClientFactory
from twisted.internet import ssl
from twisted.web import server, resource
from twisted.internet import reactor

import json
import pickle

from janecore.ircbot.ansible.protocol import AnsibleClientProtocol
from janecore.ircbot.ansible import commands

global factory # Yeah, yeah.

class Simple(resource.Resource):
    isLeaf = True

    def render_POST(self, request):
        """ Parse post message from Stash's webhooks plugin """
        body = json.loads(request.content.read())
	name = body['changesets']['values'][0]['toCommit']['author']['name']   
	commitMessage = body['changesets']['values'][0]['toCommit']['message']
        projectName = body['repository']['name']
        refstring = body['refChanges'][0]['refId']
        url = "https://stash.tfoundry.com%s" % body['changesets']['values'][0]['link']['url']

        irc_string = "\x02{user}\x02 pushed a commit to \x034[{project}]\x03\x032[{ref}]\x03:\"{message}\", {link}".format(
             user=name, 
             project=projectName,
             ref=refstring.split("/")[-1],
             message=commitMessage,
             link=url)
        new_data = ['#bots', irc_string]
        factory.p.callRemote(commands.DispatchEvent, event_name="ircDoMsg", data=pickle.dumps(new_data))
        return irc_string

class AnsibleClientFactory(ClientFactory):
    protocol = AnsibleClientProtocol
    
    def buildProtocol(self, addr):
        self.p = self.protocol()
        self.p.factory = self
        return self.p

factory = AnsibleClientFactory()
site = server.Site(Simple())
reactor.listenTCP(0, site)
reactor.connectSSL("localhost", 0, factory, ssl.ClientContextFactory())
reactor.run()
