from mint.components import Entity
from mint.components import Port

class Endpoint(Entity):

    def __init__(self, name=None):
        super(Endpoint, self).__init__(name)
        self.install(Port())
        self.port = self.ports[0]
