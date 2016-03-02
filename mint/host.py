from node import Node

class Host(Node):

    def __init__(self):
        super(Host, self).__init__(n_tips=1)

    def send(self, s):
        return self.tip.send(s)

    def recv(self, f):
        self.on_recv = f

    def on_recv(self, data):
        print '{} recved "{}" at {}'.format(self, data, self.env.now)

    def process(self, ev):
        self.on_recv(ev.data)
