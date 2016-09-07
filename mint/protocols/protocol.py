class Protocol(object):

    def __init__(self, master=None):
        self.master = master
        if master:
            master += self

    def on_send(self, ev):
        pass

    def on_recv(self, ev):
        pass

    def post(self, ev):
        return self.master.env.post(ev)

class Log(Protocol):

    def on_send(self, ev):
        print '{} send "{}" at {}'.format(self.master, ev.data, ev.now)

    def on_recv(self, ev):
        print '{} recv "{}" at {}'.format(self.master, ev.data, ev.now)
