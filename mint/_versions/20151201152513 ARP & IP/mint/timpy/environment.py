import threading
import functools
from collections import deque

import events
import utils
from utils import put, each, bunch

def check_started(f):
    @functools.wraps(f)
    def f_(self, *args, **kwargs):
        if not self.started:
            self.start()
        setattr(self, f.__name__, f.__get__(self, type(self)))
        return f(self, *args, **kwargs)
    return f_

class Environment(object):

    # step granularity
    Time = 2
    Priority = 1
    Thread = 0

    def __init__(self):
        self.threads = []
        self.timeline = build_timeline()
        self.now = 0
        self.started = False

    @property
    def finished(self):
        if not self.started:
            return False
        return all(each(self.threads).finished)

    @finished.setter
    def finished(self, val):
        self._finished = val

    @check_started
    def run(self):
        while not self.finished:
            self.step()

    @check_started
    def step(self, by=None):
        if by is None:
            by = self.Time
        threads = self.timeline.get(depth=by)
        self.now = threads[0].current_event.now
        each(threads).resume()

    def start(self):
        each(self.threads).start()
        self.started = True

    def process(self, *f, **kwargs):
        def process_(f):
            thread = Thread(self, f, **kwargs)
            self.threads.append(thread)
        return process_(f[0]) if f else process_

    def priority(self, val):
        return self.process(priority=val)

    def timeout(self, laps):
        self.schedule(events.Timeout(self, laps)).wait()

    def event(self):
        return events.Event(self)

    def schedule(self, event):
        if event.now is None:
            event.now = self.now
        self.timeline.put(event)
        event.scheduled = True
        return event

class Thread(object):

    def __init__(self, env, f, name=None, priority=0, daemon=False):
        if name is None:
            name = getattr(f, __name__, 'unknown')
        self.name = name
        self.priority = priority
        self.current_event = None
        self.blocked = threading.Event()
        self.resumed = threading.Event()
        self.thread = threading.Thread(target=Thread.wrapped(env, f))
        # the actual threading.Thread is all daemon
        self.thread.daemon = True
        # Thread.daemon means not accounting in env.finished status
        # i.e. when all non-daemon Thread is finished, env.finished == True
        self.daemon = daemon
        self.thread.master = self
        self.ending = False

    @property
    def finished(self):
        return self.daemon or not self.thread.is_alive()

    def start(self):
        self.thread.start()
        self.until_blocked()

    def block(self, ending=False):
        self.blocked.set()
        self.ending = ending
        if not ending:
            self.resumed.wait()
            self.resumed.clear()

    def resume(self):
        self.resumed.set()
        self.until_blocked()

    def until_blocked(self):
        self.blocked.wait()
        self.blocked.clear()
        if self.ending:
            self.thread.join()

    @staticmethod
    def wrapped(env, f):
        def f_():
            env.schedule(events.Initialize(env, env.now)).wait()
            f()
            threading.current_thread().master.block(ending=True)
        return f_

    def __repr__(self):
        return '{} {}'.format(self.name, self.current_event.name)

from batchheap import BatchHeap
from containerstack import ContainerStack
def build_timeline():

    def cvt(events, waiters):
        for event in events.get():
            event.trigger()
            for waiter in event.waiters:
                waiters.put(waiter)

    r = ContainerStack()
    r.add_layer(container=BatchHeap(lambda x,y: x.now < y.now),
                get=BatchHeap.pop,
                put=BatchHeap.push,
                broker=cvt)
    r.add_layer(container=BatchHeap(lambda x,y: x.priority > y.priority),
                get=BatchHeap.pop,
                put=BatchHeap.push)
    r.add_layer(container=deque(),
                get=deque.popleft,
                put=deque.extend)
    return r

env = Environment()
