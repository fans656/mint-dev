from collections import deque

import mint
from mint.core import Entity
from mint import utils

class NIC(Entity):

    class FrameTooLarge(Exception): pass

    FLAG = (0,1,1,1,1,1,1,0)
    STUFFING = (1,1,1,1,1,0)
    SUCCESSIVE = (1,1,1,1,1)

    def __init__(self, host):
        super(NIC, self).__init__(name=host.name, n_ports=1)
        self.host = host
        self.port = self.ports[0]
        self._max_frame_size = 64
        self.buffer_size = self._max_frame_size * 8
        self._obuffer_used = 0
        self._ibuffer_used = 0
        self._oframes = deque()
        self._iframes = deque()
        self._oframe = deque()
        self._iframe = deque()
        self._in_frame = False
        self.n_detected_frames = 0
        self.n_handed_frames = 0
        self.n_dropped_frames = 0
        self.dropped_frame = None
        self.frame_ended = False

    def send(self, frame):
        if len(frame) > self._max_frame_size:
            raise NIC.FrameTooLarge()
        while not self.fit(frame, self._obuffer_used):
            mint.wait(0)
        self._oframes.append(frame)
        self._obuffer_used += len(frame)

    def recv(self):
        while True:
            try:
                frame = self._iframes.popleft()
                self._ibuffer_used -= len(frame)
                return frame
            except IndexError:
                mint.wait(0)

    def run(self):
        self._flag_detector = utils.PatternDetector(self.FLAG)
        self._stuffing_bit_detector = utils.PatternDetector(self.STUFFING)
        self._successive_bits_detector = utils.PatternDetector(self.SUCCESSIVE)
        while True:
            # output phase and input phase correspond to
            # the two network.step(workers)
            # so wait(0) means go to next input phase (from output phase)
            # or go to next output phase (from input phase)
            # use context manager like this will increase the readability
            # it's actually just wait(0) in __exit__ of the context manager
            with mint.output_phase:
                if not self._oframe:
                    self.pull_frame()
                try:
                    obit = self._oframe.popleft()
                except IndexError:
                    obit = 0
                self.port.send(obit)
            with mint.input_phase:
                ibit = self.port.recv()
                self.process_input(ibit)

    def pull_frame(self):
        try:
            frame = self._oframes.popleft()
            self._obuffer_used -= len(frame)
            self._oframe.clear()
            self._oframe.extend(self.FLAG)
            for byte in frame:
                for bit in utils.to_bits(ord(byte)):
                    self._oframe.append(bit)
                    if self._successive_bits_detector.feed(bit):
                        self._oframe.append(0)
            self._successive_bits_detector.clear()
            self._oframe.extend(self.FLAG)
        except IndexError:
            pass

    def process_input(self, ibit):
        self.frame_ended = False
        if not self._in_frame:
            if self._flag_detector.feed(ibit):
                self._in_frame = True
        else:
            flag = self._flag_detector.feed(ibit)
            stuffing = self._stuffing_bit_detector.feed(ibit)
            if flag or not stuffing:
                self._iframe.append(ibit)
                if flag:
                    self.n_detected_frames += 1
                    self.frame_ended = True
                    frame = ''.join(chr(utils.to_byte(bits))
                            for bits in utils.group(self._iframe, 8))[:-1]
                    if self.fit(frame, self._ibuffer_used):
                        self.handout(frame)
                    else:
                        self.discard(frame)
                    self._iframe.clear()
                    self._in_frame = False

    def fit(self, frame, n_used):
        return self.buffer_size - n_used >= len(frame)

    def handout(self, frame):
        self.n_handed_frames += 1
        self._iframes.append(frame)
        self._ibuffer_used += len(frame)

    def discard(self, frame):
        self.n_dropped_frames += 1
        self.dropped_frame = list(frame)
