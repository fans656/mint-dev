from mint import Host
from protocols import StopAndWait

class PC(Host):

    def __init__(self):
        super(PC, self).__init__()
        self.top = StopAndWait(self, self.nic)
