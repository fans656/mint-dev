import itertools

import simpy

from mint.components import Entity, Port, Link
from mint import utils

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
        s = '<Network>\n'
        for port in self.ports:
            s += '{}\n\to:{:20}, i:{}\n'.format(str(port), port.obuffer, port.ibuffer)
        return s
