from collections import deque, OrderedDict

from bitarray import bitarray

import mint
from mint.exceptions import Full, Empty
from mint.snippets import block_on
from mint.protocols.algorithms import bitstuff

class Buffer(object):

    def __init__(self, size):
        self.size = size
        self.used = 0
        self.items = deque()

    @property
    def unused(self):
        return self.size - self.used

    def append(self, data):
        if len(data) > self.unused:
            raise Full
        self.items.append(data)
        self.used += len(data)

    def popleft(self):
        if not self.items:
            raise Empty
        item = self.items.popleft()
        self.used -= len(item)
        return item

    def __str__(self):
        return '{} {}/{}'.format(list(self.items), self.used, self.size)

class Delimiter(object):

    def __init__(self, tip, buffer_size=512):
        tip.master = self
        self.tip = tip
        self.obuffer = Buffer(buffer_size)
        self.ibuffer = Buffer(buffer_size)
        self.odata = ''
        self.idata = ''

    @block_on(Full)
    def send(self, data):
        self.odata = data
        self.obuffer.append(data)

    @block_on(Empty)
    def recv(self):
        return self.ibuffer.popleft()

    @property
    def status(self):
        return OrderedDict([
            ('obuffer', str(self.obuffer)),
            ('ibuffer', str(self.ibuffer)),
        ])

class BitDelimiter(Delimiter):

    def __init__(self, *args, **kwargs):
        super(BitDelimiter, self).__init__(*args, **kwargs)
        self.oframe = Outputter()
        self.iframe = Inputter()
        mint.worker(self.run)

    def run(self):
        while True:
            self.output()
            self.input()
            mint.elapse(1)

    def output(self):
        if not self.oframe:
            try:
                payload = self.obuffer.popleft()
                self.oframe = Outputter(payload)
            except Empty:
                pass
        self.tip.osymbol = self.oframe.next_bit()

    def input(self):
        self.iframe.feed(self.tip.isymbol)
        if self.iframe.complete:
            payload = self.iframe.tobytes()
            self.idata = payload
            try:
                self.ibuffer.append(payload)
            except Full:
                mint.report('frame dropped: {}', repr(payload))
            self.iframe = Inputter()

    @property
    def status(self):
        r = super(BitDelimiter, self).status
        s_oframe = str(self.oframe.bits[self.oframe.i:])[10:-2]
        s_iframe = str(self.iframe.bits)[10:-2]
        r.update(OrderedDict([
            ('oframe', s_oframe),
            ('iframe', s_iframe),
            ('i_count', self.iframe.count)
        ]))
        return r

    @property
    def sending(self):
        return self.oframe.frame_length

    @property
    def sent(self):
        return self.oframe.frame_length - len(self.oframe)

class Outputter(object):

    def __init__(self, bytes=None):
        if bytes is None:
            self.bits = bitarray(endian='big')
        else:
            self.bits = bitstuff.stuffed(bytes)
        self.frame_length = len(self.bits)
        self.i = 0

    def next_bit(self):
        try:
            r = self.bits[self.i]
            self.i += 1
            return int(r)
        except IndexError:
            del self.bits[:]
            self.frame_length = 0
            self.i = 0
        return 0

    def __len__(self):
        return self.frame_length - self.i

class Inputter(object):

    def __init__(self):
        self.bits = bitarray(endian='big')
        self.idle = True
        self.complete = False
        self.count = 0
        self.recving_finished = False

    def feed(self, bit):
        if self.idle:
            if bit:
                self.count += 1
            else:
                if self.count == 6:
                    mint.report('start sending')
                    self.idle = False
                self.count = 0
        else:
            self.bits.append(bit)
            if bit:
                self.count += 1
            else:
                if self.count == 5:
                    del self.bits[-1]
                elif self.count == 6:
                    del self.bits[-8:]
                    mint.report('finish recving')
                    self.complete = True
                self.count = 0

    def tobytes(self):
        return self.bits.tobytes()
