from collections import deque
from functools import partial

import mint
from mint.core import Entity

def append_to(buf, data):
    buf.append(data)

def pop_from(buf):
    while True:
        try:
            return buf.popleft()
        except IndexError:
            mint.wait()

class Protocol(Entity):

    def __init__(self, master, servant):
        super(Protocol, self).__init__()
        self.master = master
        self.servant = servant
        self.host = getattr(self.master, 'host', self.master)
        self.obuffer = deque()
        self.ibuffer = deque()
        self.send = partial(append_to, self.obuffer)
        self.recv = partial(pop_from, self.ibuffer)
        self.push = partial(append_to, self.ibuffer)
        self.pull = partial(pop_from, self.obuffer)
        self.debug_send_func = None
        self.debug_recv_func = None

    def __repr__(self):
        return '<{} of {}>'.format(
                super(Protocol, self).__repr__(), self.host)

    def compose(self, header, payload='', tail=''):
        if self.debug_send_func:
            self.debug_send_func(header, payload, tail, **{
                'host': self.host,
                'protocol': self,
                'type': 'send'})
        return header + payload + tail

    def decompose(self, data):
        if self.TAIL_SIZE:
            ret = (data[:self.HEADER_SIZE],
                    data[self.HEADER_SIZE:-self.TAIL_SIZE],
                    data[-self.TAIL_SIZE:])
        else:
            ret = (data[:self.HEADER_SIZE],
                    data[self.HEADER_SIZE:],
                    '')
        if self.debug_recv_func:
            self.debug_recv_func(*ret, **{
                'host': self.host,
                'protocol': self,
                'type': 'recv'})
        return ret

    def debug(self, f):
        self.debug_send(f)
        self.debug_recv(f)
        return f

    def debug_send(self, f):
        self.debug_send_func = f
        return f

    def debug_recv(self, f):
        self.debug_recv_func = f
        return f
