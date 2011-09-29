======
JANE
======
-------------------------------------------------------------
A multi-featured, semi-distributed IRC Bot (yes, another one)
-------------------------------------------------------------

Introduction
=============

Jane is yet another IRC bot written in python and Twisted. She is
currently in a prototype state so her api may change rapidly, drastically
and without notice. 



Features
++++++++

- Support for most IRC commands
- A simple 'local' plugin system
- A simple 'remote' plugin system (Ansible)


TODO 
++++
- Enable load,unload,reload of local plugins
- Enable authentication for remote plugins
- HTTP interface to many IRC functionalities
- Tests, documentation, and clean up


How it works
============

Factories and Protocols
+++++++++++++++++++++++

A basic understanding of Twisted's architecture is beneficial. Basically a 'server' or 'client' is represented by a Factory. A connection to or from this server or client is
called a Protocol, and is where the bulk of our logic is located (generally triggered by a ``dataReceived`` or similar event). There is generally only a single instance of a Factory, while there
can be many Protocol instances. A crude diagram of a server would look something liket he following.

::

          Protocol  -> Transport -> Client
 Factory /
         \ Protocol -> Transport -> Client


With that in mind, Jane is made up of multiple factories. 
.. Note::
    Most factories will have a class variable called protocol which will be a reference to the protocol type that this factory uses to manage it's connections.

- ``janecore.ircbot.factory.JaneIRCClient``

  This factory is responsible for creating and maintaining connections
  to IRC servers. Since it's a sort-of parent object for the protocols
  it's also use to maintain references to shared resources, specifically
  the aptly name "storage" object which holds the all important evt_mgr. 

- ``janecore.ircbot.ansible.AnsibleFactory``

  This factory is responsible for creating and maintaining an open port to which
  AnsibleClients can connect. AnsibleClients are the remote plugin applications which 
  are used to extend Jane's functionality. 

- ``janecore.web.HTTPServerFactory (Coming Soon!)``

  This Factory will be responsible for Accepting and maintaining HTTP requests from web
  browsers and other applications which speak HTTP. 

Event System
++++++++++++

The ircbot functionality is largely driven by an event manager ``janecore.eventmanager.EventManager`` which is responsible for creating, dispatching and maintaining events. Currently teh JaneIRCClient mentioned in the previous section holds the only EventManager instance as ``evt_mgr`` 

The basic workflow for this event manager is as follows. 


1. Create a module in ``janecore.events`` and in it ``import janecore.events.irc.IRCEventList``
2. Instanciate to a variable an instance of IRCEventList with a list of strings representing your events
3. When the EventManager is instantiated it will automatically load your events module and create event objects for the strings in your ``IRCEventList`` instance!
4. (Optionally) You can pass a string to ``evt_mgr.registerEventFromName()``, or create a subclass of ``janecore.eventmanager.Evt`` and pass it to ``evt_mgr.register()``
5. After you've registered an Event with the Event Manager you'll want to register a Listener for this event. Do this by calling ``evt_mgr.addListener("event_name", SomeObject)`` where ``"event_name""`` is the string associated with the event, and ``SomeObject`` is either a callable or (oh god!) an object with callable attributes named either event_name+"Callback" or just "callback".
6. FIXME: there is no explict definition of what data argument is expected. Next you can dispatch an event using ``evt_mgr.dispatch("event_name", data)`` where ``data`` is some predetermined data format such as a list or a string.

