from mint import Host
from slidingwindow import SlidingWindow

class PC(Host):

    def __init__(self):
        super(PC, self).__init__()
        self.top = SlidingWindow(self, self.nic)
