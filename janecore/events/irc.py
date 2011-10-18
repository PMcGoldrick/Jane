""" 
Note that not all of these events are consumed
or implemented:

"""
from zope.interface import implements
from twisted.plugin import IPlugin
from ..eventmanager.interface import IEventList, IRespondingEventList

class IRCEventList(list):
    implements(IPlugin, IEventList)

class IRCRespondingEventList(list):
    implements(IPlugin, IRespondingEventList)

events = {
"ircYourHost":["info"],
"ircCreated" :["info"],
"ircMyInfo":["servername", "version", "umodes", "cmodes"],
"ircLuserClient":["info"],
"ircBounce":["info"],
"ircIsupport":["options"], 
"ircLuserChannels":["channels"],
"ircLuserOp":["ops"],
"ircLuserMe":["info"],
"ircPrivmsg":[("user", "channel", "message")],
"ircJoined":["channel"],
"ircLeft":["channel"],
"ircNoticed":[("user", "channel", "message")],
"ircModeChanged":[("user", "channel", "being_set", "modes", "args")],
"ircPong":[("user", "secs")],
"ircSignedOn":[None],
"ircKickedFrom":[("channel", "kicker", "message")], 
"ircNickChanged":["nick"],
"ircUserLeft":[("user", "channel")], 
"ircUserQuit":[("user", "quitMessage")],
"ircUserKicked":[("kickee", "channel", "kicker", "message")],
"ircAction":[("user", "channel", "data")],
"ircTopicUpdated":[("user", "channel", "newTopic")],
"ircUserRenamed":[("oldname", "newname")], 
"ircReceivedMOTD":["motd"],
"ircConnectionLost":["reason"],

# Actions
"ircDoJoin":[("channel", "key")],
"ircDoLeave":[("channel", "reason")],
"ircDoKick":[("channel", "user", "reason")],
"ircDoInvite":[("user", "channel")],
"ircDoTopic":[("channel", "topic")],
"ircDoMode":[("chan", "set", "modes", "limit", "users", "mask")],
"ircDoSay":[("channel", "message", "length")],
"ircDoMsg":[("user", "message", "length")],
"ircDoNotice":[("user", "message")],
"ircDoAway":[("message")],
"ircDoBack":[None],
"ircDoWhois":[("nickname", "server")],
"ircDoSetNick":["nickname"],
"ircDoQuit":["message"], 
"ircDoDescribe":[("channel", "action")],
"ircDoPing":[("user", "text")],

# System Maintenance
}

# "eventName" : [[Args],[Returns]]
responding_events = {
#"ircLoadPlugin" : [["pluginName"], [bool]],
#"ircUnloadPlugin" : [["pluginName"],[bool]],
"ircLoadedPluginList" : [[None], [("pluginName",)]], 
"ircPluginList" : [[None],("pluginName")],
"ircJoinedChannelList" : [[None],[("channelNames")]],
}

irc_responding_events = IRCRespondingEventList(responding_events.keys())
irc_events=IRCEventList(events.keys())


