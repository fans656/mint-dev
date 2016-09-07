import env

class Event(object):

    def __init__(self, now=None):
        self.env = env.env
        self.now = now

    def __lt__(self, o):
        return self.now > o.now

    def __repr__(self):
        return '{} {}'.format(self.now, type(self).__name__)

    def __call__(self):
        print self

    def at(self, now):
        self.now = now

class Transmit(Event):

    def __init__(self, src, data, now=None):
        super(Transmit, self).__init__(now)
        self.src = src
        self.data = data

    def __repr__(self):
        return '{}({})'.format(super(Transmit, self).__repr__(), self.src)

class Send(Transmit):

    def __call__(self):
        if self.src.peer:
            self.src.master.on_send(self)
            self.src.peer.recv(self.data)

class Recv(Transmit):

    def __call__(self):
        self.src.master.on_recv(self)

class Timeout(Event):

    def __init__(self, delay, callback):
        super(Timeout, self).__init__()
        self.now = self.env.now + delay
        self.callback = callback

    def __call__(self):
        self.callback()
