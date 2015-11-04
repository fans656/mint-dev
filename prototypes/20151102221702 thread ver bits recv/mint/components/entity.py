from mint import network

class Entity(object):

    def __init__(self, name=None):
        self.name = name or str(id(self))
        self.ports = []
        network.network.add(self)

    def __repr__(self):
        return '<{} {}>'.format(self.__class__.__name__, self.name)

    def install(self, *ports):
        self.ports.extend(ports)
        for port in ports:
            port.entity = self
