import Queue

from mint import network
from mint import utils

class Port(object):

    def __init__(self):
        network.network.add(self)
        self.peer = None
        self.entity = None
        self.e2p_queue = Queue.Queue()
        self.p2e_queue = Queue.Queue()
        self.p2p_queue = Queue.Queue()
        self.obuffer = ''
        self.ibuffer = ''
        self.entity_buffer = ''
        self.rate = 1

    def __repr__(self):
        try:
            s_peer = ' to {}'.format(self.peer.entity)
        except AttributeError:
            s_peer = ''
        return '<Port of {}{peer}>'.format(self.entity, peer=s_peer)

    def make_peer_with(self, port):
        if self.peer != port:
            self.peer = port
            self.peer.make_peer_with(self)

    def run(self):
        if self.peer is None:
            return
        while True:
            self._send()
            self._recv()
            if network.network.env:
                network.network.env.timeout(1)

    def _send(self):
        # fetch from entity & send to peer port at specified rate
        self.obuffer += self.fetch_from(self.e2p_queue, block=False)
        #print '{} {}\n'.format(self, self.obuffer)
        bits, self.obuffer = utils.split_at(self.obuffer, self.rate)
        if bits:
            self.p2p_queue.put(bits)
        #print '{} {}\n'.format(self, bits)

    def _recv(self):
        # fetch from peer port & send to entity at specified rate
        self.ibuffer = self.fetch_from(self.peer.p2p_queue, block=False)
        bits, self.ibuffer = utils.split_at(self.ibuffer, self.rate)
        if bits:
            self.p2e_queue.put(bits)

    def fetch_from(self, queue, block=True):
        data = ''
        while not queue.empty():
            data += queue.get()
        if block and not data:
            data += queue.get()
        return data

    def send(self, data):
        self.e2p_queue.put(data)

    def recv(self, nbits=None, block=True):
        if block:
            if nbits is None:
                raise Exception('blocking recv must specify the number of bits')
            while len(self.entity_buffer) < nbits:
                self.entity_buffer += self.fetch_from(self.p2e_queue, block=True)
            bits, self.entity_buffer = utils.split_at(self.entity_buffer, nbits)
            return bits
        else:
            self.entity_buffer += self.fetch_from(self.p2e_queue, block=False)
            bits, self.entity_buffer = self.entity_buffer, ''
            return bits
