import Queue
from collections import deque

import mint
from mint.core import Entity
from mint.components import NIC

class Host(Entity):

    def __init__(self, name=None):
        self._top = None
        super(Host, self).__init__(name=name)
        self.nic = NIC(self)

    @property
    def top(self):
        return self._top

    @top.setter
    def top(self, protocol):
        self._top = protocol
        self.set_top_layer(protocol)

    def set_top_layer(self, protocol):
        self.send = protocol.send
        self.recv = protocol.recv
        self.pull = protocol.pull
        self.push = protocol.push

class Hub(Entity):

    pass
