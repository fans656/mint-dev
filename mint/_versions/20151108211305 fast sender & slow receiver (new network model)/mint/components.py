from collections import deque
import Queue

import mint
from mint.core import Entity
from mint import utils

class NIC(Entity):

    def __init__(self, host):
        super(NIC, self).__init__(name=host.name, n_ports=1)
        self.host = host
        self.port = self.ports[0]
        self.oframe = deque()
        self.iframe = deque()
        self.set_max_n_frames(8)

    def set_max_n_frames(self, n):
        self.MAX_N_FRAMES = n
        self.oframes = Queue.Queue(self.MAX_N_FRAMES)
        self.iframes = Queue.Queue(self.MAX_N_FRAMES)

    def send(self, frame):
        while True:
            try:
                self.oframes.put(frame, block=False)
                break
            except Queue.Full:
                mint.wait(0)
                continue

    def recv(self):
        while True:
            try:
                return self.iframes.get(block=False)
            except Queue.Empty:
                mint.wait(0)

    def run(self):
        while True:
            if not self.oframe:
                self.pull_frame()
            try:
                obit = self.oframe.popleft()
            except IndexError:
                obit = 0
            self.port.send(obit)
            mint.wait(0)
            ibit = self.port.recv()
            self.push_frame(ibit)
            mint.wait(0)

    def pull_frame(self):
        try:
            frame = self.oframes.get(block=False)
            for byte in frame:
                for bit in utils.to_bits(ord(byte)):
                    self.oframe.append(bit)
        except Queue.Empty:
            pass

    def push_frame(self, ibit):
        self.iframe.append(ibit)
        if len(self.iframe) == 1 * 8:
            frame = ''.join(chr(utils.to_byte(bits))
                    for bits in utils.group(self.iframe, 8))
            try:
                self.iframes.put(frame, block=False)
            except Queue.Full:
                #utils.put('{} dropped frame {}', self.host, repr(frame))
                pass
            self.iframe.clear()
