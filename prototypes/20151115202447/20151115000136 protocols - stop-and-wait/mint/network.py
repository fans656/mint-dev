import threading
import itertools
import functools
import Queue
from collections import defaultdict

import mint
from mint import utils

class Timer(object):

    def __init__(self, n_laps, callback, *args, **kwargs):
        self.n_laps = n_laps
        self.callback = functools.partial(callback, *args, **kwargs)
        self.now = -1

    def start(self):
        self.now = mint.now() + self.n_laps

    def stop(self):
        self.now = -1

    @property
    def stopped(self):
        return self.now == -1

    def trigger(self):
        self.callback()
    __call__ = trigger

class Network(object):

    class Stopped(Exception): pass

    def __init__(self):
        self.names = defaultdict(lambda: -1)
        self.debug = lambda: None
        self.timers = set()
        self.timer_threads = []
        for attr_name in ('entities', 'setups', 'outputs',
                'transfers', 'inputs', 'actors',
                'outputers', 'inputers'):
            setattr(self, attr_name, [])

    def new_name(self, entity):
        cls = entity.__class__
        self.names[cls] += 1
        return str(self.names[cls])

    def add(self, *entities):
        self.entities.extend(entities)
        self.transfers.extend(port.transfer
                for entity in entities
                for port in entity.ports)

    def actor(self, f):
        self.actors.append(make_thread(f, daemon=False))

    def worker(self, f, daemon=True):
        return make_thread(f, daemon=daemon)

    def run(self):
        self.now = 0
        self.install_callbacks()
        self.install_threads()
        self.call(self.setups)
        start_threads(self.actors, *(self.outputers + self.inputers))
        self.step(self.actors)
        for self.now in itertools.count():
            self.step(*self.outputers)
            self.call(self.outputs)
            self.call(self.transfers)
            self.call(self.inputs)
            self.step(*self.inputers)
            self.trigger_timers()
            self.debug()
            self.now += 1
            self.step(self.actors)
            if self.finished():
                break

    def finished(self):
        return not self.actors

    def install_callbacks(self):
        for e in self.entities:
            for name in ('setup', 'output', 'input', 'outputer', 'inputer'):
                getattr(self, name + 's').extend(e._mint_get_callbacks(name))

    def install_threads(self):
        self.outputers[:] = list(reversed([[self.worker(f) for f in fs]
                for fs in self.group_by_priority(self.outputers)]))
        self.inputers[:] = [[self.worker(f) for f in fs]
                for fs in self.group_by_priority(self.inputers)]

    def group_by_priority(self, fs):
        return [list(g) for _, g in itertools.groupby(fs,
            lambda f: f._mint_data.priority)]

    def call(self, fs):
        for f in fs:
            f()

    def step(self, *threads_groups):
        for threads in threads_groups:
            wait_threads(threads)

    def trigger_timers(self):
        self.timer_threads[:] = [t for t in self.timer_threads if t.is_alive()]
        threads = []
        for timer in self.timers:
            if not timer.stopped:
                if self.now == timer.now:
                    threads.append(self.worker(timer.trigger, daemon=False))
        self.timer_threads.extend(threads)
        start_threads(threads)
        wait_threads(self.timer_threads)

    def title(self):
        utils.put('=' * 25 + ' {}'.format(self.now))

    def timer(self, n_laps, callback, *args, **kwargs):
        timer = Timer(n_laps, callback, *args, **kwargs)
        self.timers.add(timer)
        return timer

    def kill(self, timer):
        self.timers.discard(timer)

def runs(entities):
    return (e.run for e in entities if hasattr(e, 'run'))

def make_thread(f, daemon):

    def f_(*args, **kwargs):
        t = threading.current_thread()
        t.inform.get()
        try:
            f()
        finally:
            t.report.put(0)

    t = threading.Thread(target=f_)
    t.inform = Queue.Queue()
    t.report = Queue.Queue()
    t.daemon = daemon
    return t

def start_threads(*tss):
    [t.start() for ts in tss for t in ts]

def wait_threads(ts):
    [t.inform.put(1) for t in ts]
    ts[:] = [t for t in ts if t.report.get()]

network = Network()
