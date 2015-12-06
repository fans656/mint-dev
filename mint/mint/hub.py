raise NotImplementedError('''
currently the link implementation does not allow frame animation
on link out of a hub
cause hub work on physical layer and has no sense of frame all together
also, the current frame animation is unfit for link with positive latency
we'll tackle this in the future
'''
import mint
from mint.core import Entity
from mint.utils import each

class Hub(Entity):

    def __init__(self, n_ports=3):
        super(Hub, self).__init__(n_ports)

    def run(self):
        while True:
            isum = sum(each(self.tips).isymbol)
            each.v(sample)(self.tips, isum)
            mint.elapse(1)

def sample(tip, isum):
    tip.osymbol = 1 if (isum - tip.isymbol) else 0
