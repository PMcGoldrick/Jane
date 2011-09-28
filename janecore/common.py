def singleton(cls):
    """ 
    Enforce single instance of decorated class 
    """
    instances = {}
    def getInstance(name="main"):
        if not name in instances.keys():
            instances[name] = cls()
        return instances[name]
    return getInstance

@singleton
class Storage:
    def __init__(self):
        self._plugin_storage = {}

    def getPluginStorage(self, name):
        if not name in self._plugin_storage:
            self._plugin_storage[name] = {}
        return self._plugin_storage[name]
