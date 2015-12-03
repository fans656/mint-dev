import threading
from utils import each, put

class Event(object):

    def __init__(self, env, now=None):
        self.env = env
        self.now = now
        self.scheduled = False
        self.waiters = []
        self.lock = threading.Lock()
        self.triggered = threading.Event()

    def trigger(self):
        if self.scheduled:
            self.triggered.set()
        else:
            self.env.schedule(self)

    def wait(self):
        t = threading.current_thread()
        with self.lock:
            self.waiters.append(t.master)
        t.master.current_event = self
        t.master.block()
        self.triggered.wait()

    @property
    def name(self):
        return type(self).__name__

    def __repr__(self):
        waiters = ', '.join(each(self.waiters).name)
        return '<{} {}{}>'.format(
            type(self).__name__,
            self.now,
            ' ({})'.format(waiters) if waiters else '',
        )

class Initialize(Event): pass

class Timeout(Event):

    def __init__(self, env, laps):
        super(Timeout, self).__init__(env, env.now + laps)
