from twisted.words.protocols.irc import IRCClient
from twisted.internet import protocol
from twisted.python import log
from zope.interface import Interface, Attribute

class IIRCPlugin(Interface):
    """ Interface to identify IRC plugins """


class JaneIRCClient(IRCClient):
 
    EVENT = ["doSay", "doKick", "doPart", "doJoin", "doAway", "doBack", "doList"]

    ##########################################################################
    ## PROPERTIES
    @property
    def nickname(self):
        """
        String representing current nickname
        """
        return self.factory.nickname
    @property
    def username(self):
        return self.factory.username

    @property
    def realname(self):
        return self.factory.realname

    @property 
    def channel(self):
        """ 
        String representing the current channel name 
        """
        return self.factory.channel
    
    @property
    def password(self):
        return self.factory.password

    @property
    def channe_list(self, server):
        try:
            chan_list = getattr(self.factory.storage, server)["chan_list"]
        except KeyError:
            chan_list = {}
            server_entry={"chan_list" : {}}
            setattr(self.factory.storage, server, server_entry)
        finally:
            return chan_list

    @property
    def evt_mgr(self):
        return self.factory.storage.evt_mgr

    #########################################################################
    ## COMMANDS
    ## 

    def channelList(self):
        """ 
        Get a list of channels on the server

        """
        self.sendLine("LIST")

    #########################################################################
    ## Client CALLBACKS
    ## 

    def signedOn(self):
        """
        Override, called when successfully signed onto the server
        """
        self.evt_mgr.dispatch("onSignedOn", None)
        for channel in self.factory.initial_channels:
            self.join(channel, self.factory.initial_channels[channel])
    
    def privmsg(self, user, channel, message):
        """ 
        Catches both private messages and channel broadcasts.
        fires events "queryMsg" and "privMsg".
        "queryMsg", [user, channel, message] : fired on a query
        "privMsg", [user, channel, message]  : fired on a channel broadcast
        """
        if channel == self.nickname:
            self.evt_mgr.dispatch("queryMsg", 
                                    [user, channel, message])
        else:
            self.evt_mgr.dispatch("privMsg",
                    [user, channel, message])
        self.evt_mgr.dispatch("msg", [user, channel, message])
    
    def joined(self, channel):
        self.evt_mgr.dispatch('joined', channel)

    def channelList(self):
        """
        Get a list of channels on the server

        """
        self.sendLine("LIST")

    def receivedList(self, server, channel):
        """
        I am called when the server sends part of the channel listing
        @type server: C{str}
        @param server: A string rep of the servers hostname
        @type channel: C{list}
        @param channel: A list of strings containing the clients nick,
        channel name, number of occupants (string), channel topic.
        """
        log.msg("received list %s %s" % (server, channel))
    #########################################################################
    ## Event System Callbacks
    ## 

    def doSayCallback(self, evt):
        log.msg("doSaycallback fired", evt.data)
        sender, channel, message = evt.data
        if channel == self.nickname:
            self.msg(sender.split("!")[0], message)
        else:
            self.msg(channel, message)
        return evt

    def doJoinCallback(self, evt):
        log.msg("Caught but not implemented: %s" % evt.EVENT)
        return evt

    def doPartCallback(self, evt):
        log.msg("Caught but not implemented: %s" % evt.EVENT)
        return evt

    def doKickCallback(self, evt):
        log.msg("Caught but not implemented: %s" % evt.EVENT)
        return evt

    def doAwayCallback(self, evt):
        log.msg("Caught but not implemented: %s" % evt.EVENT)
        return evt

    def doBackCallback(self, evt):
        log.msg("Caught but not implemented: %s" % evt.EVENT)
        return evt

    def doListCallback(self, evt):
        log.msg("Caught but not implemented: %s" % evt.EVENT)
        return evt

    #########################################################################
    ## Boiler Plate
    ##

    def irc_RPL_LIST(self, prefix, params):
        """ 
        Method to handle channel listing 
        """
        self.receivedList(prefix, params)

    def irc_RPL_LISTEND(self, prefix, params):
        self.receivedListEnd()

    def irc_RPL_LISTSTART(self, prefix, params):
        self.receivedListStart()

    def receivedListStart(self):
        """ 
        I am fired when RPL_LISTSTART is received
        """
        log.msg("List Started")

    def receivedListEnd(self):
        """
        I am fired when RPL_LISTEND is received
        """
        log.msg("List ended")

    def receivedList(self, server, channel):
        """
        I am called when the server sends part of the channel listing
        @type server: C{str}
        @param server: A string rep of the servers hostname
        @type channel: C{list}
        @param channel: A list of strings containing the clients nick,
        channel name, number of occupants (string), channel topic.
        """
        log.msg("received list %s %s" % (server, channel))

