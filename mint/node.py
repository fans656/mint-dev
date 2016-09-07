import Queue
from obj import Obj
from tip import Tip
from f6 import each

class Node(Obj):

    def __init__(self, n_tips):
        super(Node, self).__init__()
        assert n_tips > 0
        self.tips = [Tip(master=self) for _ in xrange(n_tips)]
        self.tip = self.tips[0]
        self.protos = []

    def on_send(self, ev):
        each(self.protos).on_send(ev)

    def on_recv(self, ev):
        each(self.protos).on_recv(ev)

    def __iadd__(self, proto):
        self.protos.append(proto)
        proto.master = self
        return self
