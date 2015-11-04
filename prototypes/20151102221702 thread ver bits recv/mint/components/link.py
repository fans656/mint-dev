from mint.components import Entity
from mint.components import Port
from mint.components import Endpoint
from mint import network, utils

class Link(Entity):

    def __init__(self, port1, port2, name=None):
        super(Link, self).__init__(name)
        self.install(Port(), Port())
        # esay usage because Endpoint has only one port
        if isinstance(port1, Endpoint):
            port1 = port1.port
        if isinstance(port2, Endpoint):
            port2 = port2.port
        self.connect(port1, self.ports[0])
        self.connect(port2, self.ports[1])
        self.latency = 3
        self.rate = 1

    def connect(self, port1, port2):
        port1.make_peer_with(port2)

    def run(self):
        preamble = '0' * self.latency
        self.pipes = {self.ports[0]: preamble, self.ports[1]: preamble}
        while True:
            network.network.env.timeout(1)
            self.transfer(self.ports[0], self.ports[1])
            self.transfer(self.ports[1], self.ports[0])

    def transfer(self, port1, port2):
        data = port1.recv(block=False)
        self.pipes[port1] += data or '0' * self.rate
        bits, self.pipes[port1] = utils.split_at(self.pipes[port1], self.rate)
        port2.send(bits)
