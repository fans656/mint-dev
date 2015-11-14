import struct
from collections import deque

import mint
from mint import Protocol, Host, utils, wait
from mint.utils import put

class StopAndWait(Protocol):

    HEADER_SIZE = 3
    TAIL_SIZE = 0

    SEQ_SIZE = 2
    ACK = 0x01
    NOT_ACK = 0x00

    def __init__(self, master, servant,
            resend_timeout=100):
        super(StopAndWait, self).__init__(master, servant)
        self.timer = mint.timer(resend_timeout, self.resend)
        self.acked = True
        self.sending_seq = 0
        self.expecting_seq = 0

    @mint.outputer
    def sender(self):
        while True:
            if self.acked:
                payload = self.master.pull()
                header = self.build(
                        acking=False,
                        ack=0, # meaningless
                        seq=self.sending_seq)
                self.frame = self.compose(header, payload)
                self.servant.send(self.frame)
                self.timer.start()
                self.acked = False
            else:
                mint.wait(0)

    @mint.inputer
    def recver(self):
        while True:
            frame = self.servant.recv()
            header, payload, _ = self.decompose(frame)
            header = self.unbuild(header)
            if header.acking:
                # sending frame ACKed
                if header.ack == self.sending_seq:
                    self.acked = True
                    self.sending_seq = (self.sending_seq + 1) % self.SEQ_SIZE
                    self.timer.stop()
            if payload:
                # is the expecting frame
                if header.seq == self.expecting_seq:
                    self.master.push(payload)
                    self.expecting_seq = (self.expecting_seq + 1) % self.SEQ_SIZE
                else:
                    utils.put(self.host, 'drop',
                            struct.unpack('!B', payload)[0], 'at', mint.now())
                # send ACK
                header = self.build(
                    acking=True,
                    ack=header.seq, # ack the recved frame
                    seq=0) # meaningless
                frame = self.compose(header) # no payload
                self.servant.send(frame)

    def resend(self):
        self.servant.send(self.frame)
        self.timer.start()

    def build(self, acking, seq, ack):
        info = self.ACK if acking else self.NOT_ACK
        return struct.pack('!3B', info, seq, ack)

    def unbuild(self, header):
        info, seq, ack = struct.unpack('!3B', header)
        return utils.Bunch(
                acking=info & self.ACK,
                seq=seq,
                ack=ack)
