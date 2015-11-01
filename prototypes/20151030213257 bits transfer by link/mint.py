import sys
import itertools
import simpy
import utils

class Entity(object):

    def __init__(self, name=None):
        if not name:
            name = str(id(self))
        self.name = name
        self.ports = []
        # add to network
        network.add(self)
        self.network = network

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

    def __repr__(self):
        s = '<{} of {:} to {:}>\n'.format(
                self.__class__.__name__,
                self.entity,
                self.peer.entity)
        s += '\ti:{:20} o:{:20}'.format(
                self.ibuffer,
                self.obuffer,
                )
        return s

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

    def proc(self, env):
        while True:
            self.handoff()
            yield env.timeout(1)

class Link(Entity):

    def noise_bit(self):
        return '0'

    def __init__(self, device1=None, device2=None, name=None):
        super(Link, self).__init__(name)
        self.install(Port(), Port())
        if device1 and device2:
            self.connect(device1, device2)
        self.latency = 3

    def connect(self, device1, device2):
        self.ports[0].fuse_with(device1.ports[0])
        self.ports[1].fuse_with(device2.ports[0])

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

class Network(object):

    def __init__(self):
        self.entities = []
        self.ports = []
        self.links = []
        self.env = simpy.Environment()

    def add(self, *components):
        entities, ports, links = utils.split(components,
                lambda t: isinstance(t, Entity),
                lambda t: isinstance(t, Port),
                lambda t: isinstance(t, Link))
        self.entities.extend(entities)
        self.ports.extend(ports)
        self.links.extend(links)

    def run(self, until=float('inf'), monitor=None):
        for port in self.ports:
            self.env.process(port.proc(self.env))
        for link in self.links:
            self.env.process(link.proc(self.env))
        if not monitor:
            self.env.run(until=until)
        else:
            for i in itertools.count() if until == float('inf') else xrange(until):
                monitor(self)
                self.env.run(i + 1)
            monitor(self)

    def __repr__(self):
        s = ''
        for port in self.ports:
            s += '{}\n\to:{:20}, i:{}\n'.format(str(port), port.obuffer, port.ibuffer)
        return s

def refresh():
    _module.network = Network()

#def proc(f, *args, **kws):
#    def wrapper():
#        _module.network.env.process(f(*args, **kws))
#    return wrapper

_module = sys.modules[__name__]
refresh()
