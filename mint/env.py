import threading
from f6 import each

class Timeline(object):

    def __init__(self):
        self.evs = []

    def add(self, ev):
        self.evs.append(ev)
        self.evs.sort()

    def pop(self):
        return self.evs.pop()

    def sort(self):
        self.evs.sort()

    def __getitem__(self, i):
        return self.evs[i]

    def __repr__(self):
        return repr(self.evs)

    def __nonzero__(self):
        return bool(self.evs)

class Env(object):

    def __init__(self):
        self.timeline = Timeline()
        self.now = 0
        self.finished = False
        self.fs = []

    def start(self, debug=False):
        self.timeline.sort()
        while self.timeline:
            ev = self.timeline.pop()
            # TODO: why 10 instead of 8?
            if not self.timeline or self.timeline[-1].now > ev.now:
                self.now = ev.now
            if debug:
                print ev
            ev()
            #if debug:
            #    print 'a', ev

    def post(self, ev):
        if ev.now is None:
            ev.now = self.now
        self.timeline.add(ev)

def start(*args, **kwargs):
    env.start(*args, **kwargs)

env = Env()
