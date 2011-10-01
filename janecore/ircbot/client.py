from twisted.words.protocols.irc import IRCClient
from twisted.internet import protocol
from twisted.python import log
from zope.interface import Interface, Attribute

class IIRCPlugin(Interface):
    """ Interface to identify IRC plugins """

def dispatcher(f):
    def meth(self, *args):
        if len(args) == 1:
            args = args[0]
        self.evt_mgr.dispatch("irc"+f.__name__[0].upper()+f.__name__[1:], args)
    try:
        orig_f = getattr(IRCClient, f.__name__)
        meth.__doc__ = orig_f.__doc__
    except:
        pass
    finally:
        return meth
    
class JaneIRCClient(IRCClient):
    # Events from the event manager that we listen for
    EVENT = ["ircDoJoin", "ircDoLeave", "ircDoKick", "ircDoInvite", "ircDoTopic",
             "ircDoMode", "ircDoSay", "ircDoMsg", "ircDoNotice", "ircDoAway",
             "ircDoBack", "ircDoWhois", "ircDoSetNick", "ircDoQuit", 
             "ircDoDescribe", "ircDoPing",]

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
    ## Client Event Dispatchers
    ## These should probably be programmatically generated eventually.
    
    @dispatcher
    def created(self, when):
        pass

    @dispatcher
    def yourHost(self, info):
        pass

    @dispatcher
    def myInfo(self, servername, version, umodes, cmodes):
        pass

    @dispatcher
    def luserClient(self, info):
        pass

    @dispatcher
    def bounce(self, info):
        pass

    @dispatcher
    def isupport(self, options): 
        pass

    @dispatcher
    def luserChannels(self, channels):
        pass

    @dispatcher
    def luserOp(self, ops):
        pass
    
    @dispatcher
    def luserMe(self, info):
        pass
    
    @dispatcher
    def privmsg(self, user, channel, message):
        pass  

    @dispatcher
    def joined(self, channel):
        pass
    
    @dispatcher
    def left(self, channel):
        pass

    @dispatcher
    def noticed(self, user, channel, message):
        pass

    @dispatcher
    def modeChanged(self, user, channel, being_set, modes, args):
        # Note: original implementation is being_set is ``set``, and
        # overrides the builtin in local scope
        pass
    
    @dispatcher
    def pong(self, user, secs):
        pass

    @dispatcher
    def signedOn(self):
        pass
    @dispatcher
    def kickedFrom(self, channel, kicker, message): 
        pass

    @dispatcher
    def nickChanged(self, nick):
        pass
    
    @dispatcher
    def userLeft(self, user, channel): 
        pass

    @dispatcher
    def userQuit(self, user, quitMessage):
        pass

    @dispatcher
    def userKicked(self, kickee, channel, kicker, message):
        pass

    @dispatcher
    def action(self, user, channel, data):
        pass
    
    @dispatcher
    def topicUpdated(self, user, channel, newTopic):
        pass
    
    @dispatcher
    def userRenamed(self, oldname, newname): 
        pass

    @dispatcher
    def receivedMOTD(self, motd): 
        pass

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
    def callback(self, evt):
        log.msg("Caught but not implemented: %s" % evt.EVENT)
        meth = evt.__class__.EVENT.split("ircDo")[-1].lower()
        meth = getattr(self, meth)
        meth(*evt.data)
    
    def signedOn(self):
        for channel in self.factory.initial_channels:
            self.evt_mgr.dispatch("ircDoJoin", 
                    (channel, self.factory.initial_channels[channel]))
    
    def ircDoSayCallback(self, evt):
        log.msg("doSaycallback fired", evt.data)
        sender, channel, message = evt.data
        if channel == self.nickname:
            self.msg(sender.split("!")[0], message)
        else:
            self.msg(channel, message)
        return evt
    
    def ircPrivMsgCallback(self, evt):
        if channel == self.nickname:
            self.evt_mgr.dispatch("ircQueryMsg", 
                                    [user, channel, message])
        else:
            self.evt_mgr.dispatch("ircPrivMsg",
                    [user, channel, message])
        self.evt_mgr.dispatch("ircMsg", [user, channel, message])
    
    def ircJoinedCallback(self, channel):
         self.evt_mgr.dispatch('ircJoined', channel)
    #########################################################################
    ## Boiler Plate
    ##
    def channelList(self):
        """
        Get a list of channels on the server

        """
        self.sendLine("LIST")

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

