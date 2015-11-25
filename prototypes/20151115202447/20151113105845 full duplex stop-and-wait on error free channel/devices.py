import struct
from collections import deque

import mint
from mint import Host, utils, wait
from mint.utils import put

class PC(Host):

    NOT_ACK = struct.pack('!B', 0x00)
    ACK = struct.pack('!B', 0x01)
    HEADER_SIZE = 1

    def __init__(self):
        super(PC, self).__init__()
        self.obuffer = deque()
        self.ibuffer = deque()
        self.acked = True

    def send(self, packet):
        self.obuffer.append(packet)

    def recv(self):
        while True:
            try:
                return self.ibuffer.popleft()
            except IndexError:
                mint.wait(0)

    @mint.outputer(0)
    def link_layer_sender(self):
        while True:
            if self.acked:
                data = self.pull()
                frame = self.NOT_ACK + data
                self.nic.send(frame)
                self.acked = False
            else:
                mint.wait(0)

    @mint.inputer(0)
    def link_layer_recver(self):
        while True:
            frame = self.nic.recv()
            if self.is_ack(frame):
                self.acked = True
            else:
                self.push(frame[self.HEADER_SIZE:])
                self.nic.send(self.ACK)

    def is_ack(self, frame):
        ack, = struct.unpack('!B', frame[:self.HEADER_SIZE])
        return ack & 0x01

    def pull(self):
        while True:
            try:
                return self.obuffer.popleft()
            except IndexError:
                mint.wait(0)

    def push(self, data):
        self.ibuffer.append(data)
