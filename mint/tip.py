import env
import event
from obj import Obj

class Tip(Obj):

    def __init__(self, master):
        super(Tip, self).__init__()
        self.master = master
        self.peer = None

    def send(self, data):
        if self.peer is not None:
            ev = event.Send(src=self, data=data)
            self.env.post(ev)
            return ev

    def recv(self, data):
        self.env.post(event.Recv(src=self, data=data))

    def fuse(self, peer):
        assert self.peer is None
        self.peer = peer
        peer.peer = self

    def __repr__(self):
        return '{}->{}'.format(
            self.master,
            self.peer.master)
