from zope.interface import implements
from twisted.python import log
from twisted.plugin import IPlugin

from janecore.eventmanager import IEventListener

class DittoBot:
    EVENT = ["msg", "privMsg", "queryMsg"]
    deliminator = '||'
    implements(IPlugin, IEventListener)
    """ Class that repeats a message to a channel """

    def msgCallback(self, evt):
        """ Called when prifMsg is fired """
        log.msg("msgCallback fired SHOOOP")
        self.botSay(evt.data).addErrback()
    
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
