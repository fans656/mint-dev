import threading
import itertools
import functools
import Queue
from collections import defaultdict

from mint import utils

class Network(object):

    class Stopped(Exception): pass

    def __init__(self):
        self.names = defaultdict(lambda: -1)
        self.debug = lambda: None
        self.timers = set()
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

    def worker(self, f):
        return make_thread(f, daemon=True)

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
            self.timeout()
            self.debug()
            self.now += 1
            self.step(self.actors)
            if self.finished():
                break

    def finished(self):
        return not (self.actors or self.timers)

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

    def timeout(self):
        new_timers = []
        for timer in self.timers:
            if self.now == timer.now:
                timer.callback()
            else:
                new_timers.append(timer)
        self.timers = set(new_timers)

    def title(self):
        utils.put('=' * 25 + ' {}'.format(self.now))

    def timer(self, n_laps, callback, *args, **kwargs):
        self.timers.add(utils.Bunch(
            now=self.now + n_laps,
            callback=functools.partial(callback, *args, **kwargs)))

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
