from twisted.application import service

class JaneIRCService(service.Service):
    def startService(self):
        service.Service.startService(self)
    
    def stopService(self):
        print "Stopping Services"
        #from server import factory
        #return factory.event_manager.dispatch("shutDown", None)

class AnsibleService(service.Service):
    def startService(self):
        service.Service.startService(self)

    def stopService(self):
        print "Stopping Services"
