from protocol import Protocol
from mint import event

class Retransmit(Protocol):

    def on_send(self, ev):
        if not hasattr(self, 'ev'):
            self.ev = ev
            self.post(event.Timeout(20, self.on_timeout))

    def on_timeout(self):
        self.master.send(self.ev.data)
