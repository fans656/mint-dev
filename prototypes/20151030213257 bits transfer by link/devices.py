import mint
from mint import Entity, Port
import utils

class PC(Entity):

    def __init__(self, name=None):
        super(PC, self).__init__(name)
        self.install(Port())
        self.port = self.ports[0]
