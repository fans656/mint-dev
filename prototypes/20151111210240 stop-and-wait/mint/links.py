from collections import deque

import mint
from mint.core import Entity
from mint.devices import Host

class Link(Entity):

    def __init__(self, port1=None, port2=None, name=None,
            latency=1):
        super(Link, self).__init__(name=name, n_ports=2)
        if isinstance(port1, Host):
            port1 = port1.nic.port
        if isinstance(port2, Host):
            port2 = port2.nic.port
        if port1 and port2:
            self.connect(port1, self.ports[0])
            self.connect(port2, self.ports[1])
        self.latency = latency
        self.setup()

    def setup(self):
        preamble = [0] * self.latency
        self.out0 = deque(preamble)
        self.out1 = deque(preamble)
        return self.out0, self.out1

    def connect(self, port1, port2):
        port1.peer_with(port2)

    def run(self):
        out0, out1 = self.setup()
        while True:
            self.ports[1].send(out0.popleft())
            self.ports[0].send(out1.popleft())
            mint.wait(0)
            out0.append(self.ports[0].recv())
            out1.append(self.ports[1].recv())
            mint.wait(0)
