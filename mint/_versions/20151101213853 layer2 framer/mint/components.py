from mint.signal import Signal
from mint import signal
from mint import utils
import mint

class Entity(object):

    def __init__(self, name=None):
        if not name:
            name = str(id(self))
        self.name = name
        self.ports = []
        # add to network
        self.network = mint.network
        self.network.add(self)

    def __repr__(self):
        return '<{}:{}>'.format(self.__class__.__name__, self.name)

    def install(self, *ports):
        self.ports.extend(ports)
        for port in ports:
            port.attach_to(self)
        # notify ports installation to network
        self.network.add(*ports)

class Port(object):

    def __init__(self, rate=1):
        self.entity = None
        self.peer = None
        self.rate = rate
        self.obuffer = ''
        self.ibuffer = ''
        self.bit_arrive = Signal()
        #self.bit_sent = ''
        self.bits_received = ''

    def __repr__(self):
        try:
            peer_entity = self.peer and self.peer.entity or None
            s = '<{} of {}>'.format(
                    self.__class__.__name__,
                    self.entity)
            #s = '<{} of {:} to {:}>\n'.format(
            #        self.__class__.__name__,
            #        self.entity,
            #        peer_entity)
            #s += '\ti:{:20} o:{:20}'.format(
            #        self.ibuffer,
            #        self.obuffer,
            #        )
            return s
        except Exception:
            return super(Port, self).__repr__()

    def attach_to(self, entity):
        self.entity = entity

    def fuse_with(self, port):
        self.peer = port
        if port.peer != self:
            port.fuse_with(self)

    def put(self, data, is_bits=False):
        if not is_bits:
            data = utils.bitify(data)
        self.obuffer += data

    def get(self, nbits=None):
        if not nbits:
            nbits = len(self.ibuffer)
        ret, self.ibuffer = utils.split_at(self.ibuffer, nbits)
        return ret

    def handoff(self):
        if not self.peer:
            return
        sent, self.obuffer = utils.split_at(self.obuffer,
                min(self.rate, self.peer.rate))
        self.peer.ibuffer += sent
        self.peer.bits_received += sent
        # TODO
        # this ought to be implemented like this:
        # buffer as a descriptor
        # when altered, emit the signal
        # so bit_arrive then is no need to be emitted here
        # writting the ugly self.peer... etc.
        self.peer.bit_arrive(self.peer)

    def proc(self, env):
        while True:
            self.handoff()
            yield env.timeout(1)

class Endpoint(Entity):

    def __init__(self, name=None):
        super(Endpoint, self).__init__(name)
        self.install(Port())
        self.port = self.ports[0]

class Intersection(Entity):

    def __init__(self, name=None, nports=3):
        super(Intersection, self).__init__(name)
        self.install(*[Port() for _ in range(nports)])

class Link(Entity):

    def __init__(self, port1=None, port2=None, name=None):
        super(Link, self).__init__(name)
        self.install(Port(), Port())
        if isinstance(port1, Endpoint):
            port1 = port1.port
        if isinstance(port2, Endpoint):
            port2 = port2.port
        self.connect(port1, port2)
        self.latency = 3

    def connect(self, port1, port2):
        self.ports[0].fuse_with(port1)
        self.ports[1].fuse_with(port2)

    def get_bit(self, port):
        if port.ibuffer:
            self.pipes[port] += port.ibuffer
            port.ibuffer = ''
        else:
            self.pipes[port] += self.noise_bit()
        bit, self.pipes[port] = utils.split_at(self.pipes[port], 1)
        return bit

    def transfer(self, port1, port2):
        bit = self.get_bit(port1)
        port2.put(bit, True)

    def proc(self, env):
        self.pipes = dict(zip(self.ports, [self.noise_bit() * self.latency] * 2))
        while True:
            self.transfer(*self.ports)
            self.transfer(*reversed(self.ports))
            yield env.timeout(1)

    def noise_bit(self):
        return '0'
