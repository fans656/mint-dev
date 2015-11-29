import Queue
from collections import deque

import mint
from mint.core import Entity
from mint.components import NIC
from mint.protocols import Protocol

class Host(Entity):

    def __init__(self, name=None):
        self._top = None
        super(Host, self).__init__(name=name)
        self.nic = NIC(self)
        #self.top = Protocol(self, self.nic)

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

    def __init__(self, *hosts, **kwargs):
        n_ports = len(hosts) if hosts else 3
        name = kwargs.get('name', None)
        super(Hub, self).__init__(name, n_ports)
        self.links = []
        for host, port in zip(hosts, self.ports):
            self.links.append(mint.link(host, port))

    @mint.setup
    def setup(self):
        for port in self.ports:
            port.set(0)

    @mint.input
    def input(self):
        total = sum(p.get() for p in self.ports)
        for port in self.ports:
            symbol = 1 if (total - port.get()) else 0
            port.set(symbol)

class Switch(Entity):

    class Port(object):

        def __init__(self, switch, nic):
            self.switch = switch
            self.routes = switch.routes
            self.nic = nic
            self.iframes = deque()
            self.oframes = deque()

        def setup_siblings(self):
            self.siblings = tuple(p for p in self.switch.ports if p != self)

        def recv(self):
            while True:
                try:
                    frame = self.nic.recv(block=False)
                    frame = mint.PDU.Frame(frame)
                    self.routes[frame.src_addr] = mint.utils.Bunch(
                            port=self, time=mint.now())
                    self.iframes.append(frame)
                except mint.exceptions.WouldBlock:
                    break

        def route(self):
            while len(self.iframes):
                frame = self.iframes.popleft()
                try:
                    oport = self.routes[frame.dst_addr].port
                except KeyError:
                    self.flood(frame)
                else:
                    oport.oframes.append(frame)

        def send(self):
            while len(self.oframes):
                frame = self.oframes[0]
                try:
                    self.nic.send(str(frame), block=False)
                except mint.exceptions.WouldBlock:
                    break
                else:
                    self.oframes.popleft()

        def flood(self, frame):
            for port in self.siblings:
                port.oframes.append(frame)

    def __init__(self, *hosts, **kwargs):
        super(Switch, self).__init__(kwargs.get('name', None))
        self.routes = {}
        n_ports = len(hosts) if hosts else 3
        self.nics = mint.gen(n_ports, NIC, self)
        self.ports = tuple(Switch.Port(self, nic) for nic in self.nics)
        [p.setup_siblings() for p in self.ports]
        self.links = []
        for host, nic in zip(hosts, self.nics):
            self.links.append(mint.link(host, nic.port))

    @mint.recver
    def recver(self):
        while True:
            self.switch_frames()
            mint.wait(0)

    def switch_frames(self):
        [p.recv() for p in self.ports]
        [p.route() for p in self.ports]
        [p.send() for p in self.ports]

    def show(self):
        for nic in self.nics:
            nic.show()
            mint.put()
        mint.put('-' * 20)
        for k, v in self.routes.items():
            mint.put(k, ':', v)
