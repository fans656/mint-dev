import mint
from mint import network, utils

class Port(object):

    def __init__(self, entity):
        self.entity = entity
        self.peer = None
        self.osymbol = None
        self.isymbol = None

    def io(self, osymbol=None):
        if osymbol is not None:
            self.osymbol = osymbol
        mint.wait(0)
        return self.isymbol

    def send(self, osymbol):
        self.osymbol = osymbol

    set_initial_output = send

    def recv(self):
        return self.isymbol

    def peer_with(self, port):
        if self.peer != port:
            self.peer = port
            self.peer.peer_with(self)

    def transfer(self):
        self.isymbol = self.peer.osymbol if self.peer else self.osymbol

    def show(self):
        utils.put(self)
        utils.put('\to {}', self.osymbol)
        utils.put('\ti {}', self.isymbol)

    def __repr__(self):
        try:
            s_peer = ' to {}'.format(self.peer.entity)
        except AttributeError:
            s_peer = ''
        return '<Port of {}{peer}>'.format(self.entity, peer=s_peer)

class Entity(object):

    def __init__(self, name=None, n_ports=0):
        self.name = name or network.network.new_name(self)
        self.ports = [Port(self) for _ in range(n_ports)]
        network.network.add(self)
        for mint_callback_name in ('setup', 'sender', 'recver',
                'output', 'input'):
            setattr(self, mint_callback_name + 's', [])
        for method_name in dir(self):
            method = getattr(self, method_name)
            try:
                callback_type = method._mint_data.type
            except AttributeError:
                pass
            else:
                self._mint_get_callbacks(callback_type).append(method)

    def __repr__(self):
        return '<{} {}>'.format(self.__class__.__name__, self.name)

    def _mint_get_callbacks(self, callback_type):
        return getattr(self, callback_type + 's')
