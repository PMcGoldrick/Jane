from zope.interface import implements
from twisted.python import log
from twisted.plugin import IPlugin
from twisted.internet import defer
from janecore.eventmanager import IEventListener

class DittoBot:
    EVENT = ["ircPrivmsg",]
    deliminator = '||'
    implements(IPlugin, IEventListener)
    """ Class that repeats a message to a channel """

    def ircPrivmsgCallback(self, evt):
        """ Called when prifMsg is fired """
        log.msg("msgCallback fired")
        if "list your channels" in evt.data[-1]:
            d = defer.Deferred()
            log.msg("in if")
            d.addCallback(self.channelListCallback)
            self.factory.storage.evt_mgr.dispatch("ircJoinedChannelList", None, callback_deferred=d)

    def channelListCallback(self, message):
        log.msg("Event returned", message)

    def botSay(self, data_list):
        """ Fires the doSay event with message and channel """
        return self.factory.storage.evt_mgr.dispatch("doSay", data_list)

    def load(self, factory):
        """ Called by plugin system to load this plugin """
        self.factory = factory

    def unload(self, factory):
        """ Called by plugin system to unload this plugin """
        pass

    def callback(self, evt):
        log.msg("callback method fired, %s" % evt)        
    
    def errBack(self, error):
        print "error"
        print error
ditto_plugin = DittoBot()
