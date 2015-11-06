import Queue
import functools
from collections import deque

import mint
from mint import network, utils

class Port(object):

    def __init__(self, entity):
        self.entity = entity
        self.peer = None
        self.oqueue = Queue.Queue()
        self.iqueue = Queue.Queue()
        self.obuffer = deque()
        self.ibuffer = deque()
        self.osymbol = '0'
        self.obits = []
        self.ibits = []

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
        while True:
            try:
                bits = utils.listify_bits(self.oqueue.get(block=False))
                self.obuffer.extend(bits)
            except Queue.Empty:
                break
        if not self.obuffer:
            self.obuffer.append(0)
        bit = self.obuffer.popleft()
        self.osymbol = bit
        self.obits.append(bit)

    def push(self):
        if self.peer:
            bit = self.peer.osymbol
            self.iqueue.put(bit)
            self.ibits.append(bit)

    def send(self, bits):
        self.oqueue.put(bits)

    def recv(self, nbits=0):
        '''
        Retrieve `nbits` bits from the hardware.

        If `nbits` > 0, return the bits retrieved. If there are
        no enough bits currently available, `recv` will block until
        enough bits become available.
        If `nbits` is 0, return a iterable which when iterated over
        will retrieve 1 bit at a time. Equivalent to:

            recv()
                while True:
                    yield recv(1)
        '''
        if not nbits:
            return iter(functools.partial(self.recv, 1), None)
        if not self.peer:
            # let go of unlinked port
            # e.g. a 3-ports hub linking two hosts
            return ''
        while True:
            while True:
                try:
                    self.ibuffer.append(self.iqueue.get(block=False))
                except Queue.Empty:
                    break
            if len(self.ibuffer) >= nbits:
                return ''.join('1' if self.ibuffer.popleft() else '0'
                        for _ in xrange(nbits))
            mint.wait(0)

    def show(self):
        utils.put(self, self.osymbol)
        utils.put('\to', utils.unlistify_bits(self.obits))
        utils.put('\ti', utils.unlistify_bits(self.ibits))

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
        self.pipes[port1] += bit
        bits, self.pipes[port1] = utils.split_at(self.pipes[port1], 1)
        port2.send(bits)

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
