import Queue
from obj import Obj
from tip import Tip

class Node(Obj):

    def __init__(self, n_tips):
        super(Node, self).__init__()
        assert n_tips > 0
        self.tips = [Tip(master=self) for _ in xrange(n_tips)]
        self.tip = self.tips[0]
