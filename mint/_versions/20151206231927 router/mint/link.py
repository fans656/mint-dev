from collections import deque, OrderedDict

import mint
from mint import simulation
from mint.core import Tip, Entity
from mint.host import Host
from mint.utils import each

class Link(Entity):

    def __init__(self, a, b, latency=0):
        super(Link, self).__init__(n_interfaces=2)
        a.peer_with(self.tips[0], by=self)
        self.tips[1].peer_with(b, by=self)
        self.latency = latency
        self.pipes = [deque([0] * self.latency) for _ in xrange(2)]
        self.endpoint_names = map(str, each(self.tips).peer.host)

    def peer_of(self, tip):
        return next(t for t in self.tips if t != tip.peer).peer

    def run(self):
        while True:
            self.transfer(self.tips[0], self.pipes[0], self.tips[1])
            self.transfer(self.tips[1], self.pipes[1], self.tips[0])
            mint.elapse(1)

    def transfer(self, itip, pipe, otip):
        pipe.appendleft(itip.isymbol)
        otip.osymbol = pipe.pop()

    @property
    def status(self):
        name0, name1 = self.endpoint_names
        pipe_name0 = '{} -> {}'.format(name0, name1)
        pipe_name1 = '{} -> {}'.format(name1, name0)
        return OrderedDict((
            (pipe_name0, ''.join(map(str, self.pipes[0]))),
            (pipe_name1, ''.join(map(str, self.pipes[1]))),
        ))

    # get the tip of entity which is connected by this link
    # e.g. a switch has tip-0 linked to a host by link `l`, then
    # l[switch] == switch.tips[0]
    # l[host] == host.tip
    def __getitem__(self, entity):
        return next(tip.peer for tip in self.tips if tip.peer.host == entity)

def link(a, b, *args, **kwargs):
    def to_tip(o):
        if isinstance(o, Tip):
            return o
        try:
            return next(t for t in o.tips if not t.peer)
        except StopIteration:
            raise ValueError('no available tip on {}'.format(o))
    return Link(to_tip(a), to_tip(b), *args, **kwargs)
