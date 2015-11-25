from collections import deque
import mint
from mint import simulation, utils
from mint.utils import bunch

class Tip(object):

    def __init__(self):
        self.peer = None
        self._osymbol = 0
        self.isymbol = 0

    @property
    def osymbol(self):
        return self._osymbol

    @osymbol.setter
    def osymbol(self, symbol):
        self._osymbol = symbol
        if self.peer:
            self.peer.isymbol = symbol

    def peer_with(self, tip):
        self.peer = tip
        self.peer.peer = self

    @property
    def status(self):
        return bunch(isymbol=self.isymbol, osymbol=self.osymbol)

class Entity(object):

    def __init__(self, n_tips):
        self.tips = [Tip() for _ in xrange(n_tips)]
        mint.add(self)

    def __repr__(self):
        return '{} {}'.format(type(self).__name__, self.index)

class NIC(object):

    def __init__(self, tip):
        super(NIC, self).__init__()
        self.tip = tip
        self.oframes = deque()
        self.iframes = deque()
        mint.process(self.run, priority=simulation.NIC_PRIORITY)

    def send(self, data):
        self.oframes.append(data)

    def recv(self):
        while True:
            try:
                return self.iframes.popleft()
            except IndexError:
                mint.elapse(1)

    def run(self):
        while True:
            try:
                frame = self.oframes.popleft()
            except IndexError:
                frame = 0
            self.tip.osymbol = frame
            if self.tip.isymbol != 0:
                self.iframes.append(self.tip.isymbol)
            mint.elapse(1)

    @property
    def status(self):
        return bunch(
            oframes=self.oframes,
            iframes=self.iframes,
            tip=self.tip,
        )

class Host(Entity):

    role = 'Host'

    def __init__(self):
        super(Host, self).__init__(n_tips=1)
        self.nic = NIC(self.tips[0])

    @property
    def status(self):
        return bunch(nic=self.nic)

class Link(Entity):

    role = 'Link'

    def __init__(self, a, b, latency=1):
        super(Link, self).__init__(n_tips=2)
        # there's an inherent latency of 1 due to the simulation model
        if latency < 1:
            latency = 1
        latency -= 1
        self.latency = latency
        a.peer_with(self.tips[0])
        b.peer_with(self.tips[1])
        mint.process(self.run, priority=simulation.LINK_PRIORITY)

    def run(self):
        initial = [0] * self.latency
        pipe0to1 = deque(initial)
        pipe1to0 = deque(initial)
        while True:
            self.transfer(self.tips[0], self.tips[1], pipe0to1)
            self.transfer(self.tips[1], self.tips[0], pipe1to0)
            mint.elapse(1)

    def transfer(self, itip, otip, dq):
        dq.append(itip.isymbol)
        otip.osymbol = dq.popleft()

    @property
    def status(self):
        return bunch(latency=self.latency)

def link(a, b, *args, **kwargs):
    def to_tip(o):
        if isinstance(o, Host):
            return o.nic.tip
        elif isinstance(o, NIC):
            return o.tip
        elif isinstance(o, Tip):
            return o
    return Link(to_tip(a), to_tip(b), *args, **kwargs)
