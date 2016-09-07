import event
from node import Node

class Link(Node):

    def __init__(self, a, b, delay=0):
        super(Link, self).__init__(n_tips=2)
        self.delay = delay
        self.a = a
        self.a_tip = self.tips[0]
        self.a.fuse(self.a_tip)
        self.b = b
        self.b_tip = self.tips[1]
        self.b.fuse(self.b_tip)

    def on_recv(self, ev):
        src = self.other_end(ev.src)
        data = ev.data
        now = ev.now + self.delay
        ev = event.Send(src=src, data=data, now=now)
        self.env.post(ev)

    def other_end(self, tip):
        return self.tips[1] if self.tips[0] == tip else self.tips[0]

def link(a, b, *args, **kwargs):
    return Link(to_tip(a), to_tip(b), *args, **kwargs)

def to_tip(o):
    if hasattr(o, 'tip'):
        return o.tip
    else:
        return o
