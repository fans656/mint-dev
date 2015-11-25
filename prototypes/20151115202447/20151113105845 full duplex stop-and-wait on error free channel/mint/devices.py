import Queue
from collections import deque

import mint
from mint.core import Entity
from mint.components import NIC

class Host(Entity):

    def __init__(self, name=None):
        super(Host, self).__init__(name=name)
        self.nic = NIC(self)

class Hub(Entity):

    pass
