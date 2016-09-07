from node import Node
from protocols.protocol import Log

class Host(Node):

    def __init__(self):
        super(Host, self).__init__(n_tips=1)
        Log(self)

    def send(self, data):
        return self.tip.send(data)

    def recv(self, f):
        self.on_recv = f
