import struct
from collections import deque

import mint
from mint import Protocol, utils

RESEND = 0

class SlidingWindow(Protocol):

    ACK = 0x01
    NOT_ACK = 0x00
    MAX_SEQ = 0xff

    HEADER_SIZE = 3

    def __init__(self, master, servant,
            swnd_size=1,
            rwnd_size=1,
            resend_timeout=100):
        super(SlidingWindow, self).__init__(master, servant)
        self.swnd_size = swnd_size
        self.rwnd_size = rwnd_size
        self.resend_timeout = resend_timeout
        self.oframes = deque()
        self.oseq = 0
        self.ipayloads = [None] * rwnd_size
        self.iseq_beg = 0
        self.iseq_end = 1

    @mint.sender
    def sender(self):
        while True:
            while self.events:
                e = self.events.popleft()
                if e.type == RESEND:
                    self.servant.send(frame)
                    e.timer.start()
            if self.allowed_to_send():
                payload = self.master.pull()
                header = self.build(seq=self.oseq)
                frame = self.compose(header, payload)
                self.servant.send(frame)
                timer = self.timer(self.resend_timeout,
                        utils.Bunch(type=RESEND, frame=frame, acked=False))
                self.oframes.append(utils.Bunch(seq=self.oseq, timer=timer))
                self.oseq = (self.oseq + 1) & self.MAX_SEQ
            else:
                mint.wait(0)

    @mint.recver
    def recver(self):
        while True:
            frame = self.servant.recv()
            header, payload, _ = self.decompose(frame)
            header = self.unbuild(header)
            if header.acking:
                frame = next((t for t in self.oframes if header.ack == t.seq), None)
                if frame:
                    frame.acked = True
                    frame.timer.kill()
                    while self.oframes and self.oframes[0].acked:
                        self.oframes.popleft()
            if payload:
                if self.inbound(header.seq, self.iseq_beg, self.iseq_end, self.rwnd_size):
                    index = (header.seq + self.rwnd_size - self.iseq_beg) % self.rwnd_size
                    self.ipayloads[index] = payload
                    if header.seq == self.iseq_beg:
                        self.master.push(payload)
                        self.iseq_beg = (self.iseq_beg + 1) & self.MAX_SEQ
                        self.iseq_end = (self.iseq_end + 1) & self.MAX_SEQ
                self.acknowledge(header.seq)

    def allowed_to_send(self):
        return len(self.oframes) < self.swnd_size

    def build(self, seq=0, acking=False, ack=0):
        info = 0x00
        info |= self.ACK if acking else self.NOT_ACK
        return struct.pack('!3B', info, seq, ack)

    def unbuild(self, header):
        info, seq, ack = struct.unpack('!3B', header)
        return utils.Bunch(
                acking=info & self.ACK,
                seq=seq,
                ack=ack)

    def inbound(self, i, b, e, n):
        if e < b:
            e += n
        return b <= i <= e

    def acknowledge(self, seq):
        self.servant.send(self.build(acking=True, ack=seq))
