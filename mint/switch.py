from node import Node
from f6 import each

class Switch(Node):

    def __init__(self, n_tips=3):
        super(Switch, self).__init__(n_tips=n_tips)

    def process(self, ev):
        each(self.other_tips(ev.src)).send(ev.data)

    def other_tips(self, tip):
        return [t for t in self.tips if t is not tip]
