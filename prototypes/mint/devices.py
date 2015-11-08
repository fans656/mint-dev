import Queue
from collections import deque

import mint
from mint.core import Entity
from mint.components import NIC

class Host(Entity):

    def __init__(self, name=None):
        super(Host, self).__init__(name=name)
        self.nic = NIC(self)
        self.port = self.nic.port

    def send(self, data):
        self.nic.send(data)

    def recv(self, n_bits):
        bits = deque()
        while len(bits) < n_bits:
            try:
                bit = self.nic.ibuffer.get(block=False)
                bits.append(bit)
            except Queue.Empty:
                mint.wait(0)
        return ''.join(map(str, bits))

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
