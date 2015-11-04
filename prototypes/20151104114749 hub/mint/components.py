import Queue

import mint
from mint import network, utils

class Port(object):

    def __init__(self, entity):
        self.entity = entity
        self.peer = None
        self.oqueue = Queue.Queue()
        self.iqueue = Queue.Queue()
        self.obuffer = ''
        self.ibuffer = ''
        self.osymbol = '0'
        self.ebuffer = ''

    def __repr__(self):
        try:
            s_peer = ' to {}'.format(self.peer.entity)
        except AttributeError:
            s_peer = ''
        return '<Port of {}{peer}>'.format(self.entity, peer=s_peer)

    def peer_with(self, port):
        if self.peer != port:
            self.peer = port
            self.peer.peer_with(self)

    def pull(self):
        data = ''
        while True:
            try:
                data += self.oqueue.get(block=False)
            except Queue.Empty:
                break
        self.obuffer += data or '0'

    def push(self):
        self.iqueue.put(self.ibuffer)
        self.ibuffer = ''

    def output(self):
        self.osymbol, self.obuffer = utils.split_at(self.obuffer, 1)

    def input(self):
        if self.peer:
            self.ibuffer += self.peer.osymbol
        else:
            self.ibuffer += '0'

    def send(self, data):
        self.oqueue.put(data)

    def recv(self, nbits):
        while True:
            while True:
                try:
                    self.ebuffer += self.iqueue.get(block=False)
                except Queue.Empty:
                    break
            if len(self.ebuffer) >= nbits:
                ret, self.ebuffer = utils.split_at(self.ebuffer, nbits)
                return ret
            else:
                mint.wait(0)
                continue

    def show(self):
        s = '{}:\n'.format(self)
        s += '\tosymbol {}   oqueue {}   iqueue {}\n'.format(
                self.osymbol,
                utils.view_queue(self.oqueue),
                utils.view_queue(self.iqueue),
                )
        s += '\tibuffer {}\t'.format(self.ibuffer)
        s += '\tobuffer {}\n'.format(self.obuffer)
        s += '\tebuffer {}\n'.format(self.ebuffer)
        print s[:-1]

class Entity(object):

    def __init__(self, name=None, n_ports=1):
        self.name = name or network.network.new_name(self)
        self.ports = [Port(self) for _ in range(n_ports)]
        network.network.add(self)

    def __repr__(self):
        return '<{} {}>'.format(self.__class__.__name__, self.name)

class Link(Entity):

    def __init__(self, port1=None, port2=None, name=None,
            latency=0):
        super(Link, self).__init__(name=name, n_ports=2)
        if isinstance(port1, Host):
            port1 = port1.port
        if isinstance(port2, Host):
            port2 = port2.port
        if port1 and port2:
            self.connect(port1, self.ports[0])
            self.connect(port2, self.ports[1])
        self.latency = latency

    def connect(self, port1, port2):
        port1.peer_with(port2)

    def run(self):
        preamble = '0' * self.latency
        self.pipes = {self.ports[0]: preamble, self.ports[1]: preamble}
        while not mint.stopped():
            self.transfer(self.ports[0], self.ports[1])
            self.transfer(self.ports[1], self.ports[0])

    def transfer(self, port1, port2):
        bit = port1.recv(1)
        #import random
        #bit = '1' if random.randint(0, 1) else '0'
        self.pipes[port1] += bit
        bits, self.pipes[port1] = utils.split_at(self.pipes[port1], 1)
        port2.send(bits)
        #print '{} -> {}: {}'.format(port1, port2, bits)

class Host(Entity):

    def __init__(self, name=None):
        super(Host, self).__init__(name=name, n_ports=1)
        self.port = self.ports[0]

class Hub(Entity):

    def __init__(self, name=None, n_ports=3):
        super(Hub, self).__init__(name=name, n_ports=n_ports)

    def run(self):
        while not mint.stopped():
            n = len(self.ports)
            sent_bits = ['0'] * n
            for i, port in enumerate(self.ports):
                bit = port.recv(1)
                if bit == '1':
                    for j in range(n):
                        if i != j:
                            sent_bits[j] = '1'
            for i, port in enumerate(self.ports):
                port.send(sent_bits[i])
