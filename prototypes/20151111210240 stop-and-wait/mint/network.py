import threading
import itertools
import Queue
from collections import defaultdict

from mint import utils

class Network(object):

    class Stopped(Exception): pass

    def __init__(self):
        self.entities = []
        self.ports = []
        self.actors = []
        self.workers = []
        self.names = defaultdict(lambda: -1)
        self.before_init = lambda: None
        self.after_init = lambda: None
        self.before_worker_output = lambda: None
        self.after_worker_output = lambda: None
        self.before_transfer = lambda: None
        self.after_transfer = lambda: None
        self.before_worker_input = lambda: None
        self.after_worker_input = lambda: None
        self.before_actor = lambda: None
        self.after_actor = lambda: None

    def new_name(self, entity):
        cls = entity.__class__
        self.names[cls] += 1
        return str(self.names[cls])

    def add(self, *entities):
        self.entities.extend(entities)
        self.ports.extend(port
                for entity in entities
                for port in entity.ports)

    def actor(self, f):
        self.actors.append(make_thread(f, daemon=False))

    def worker(self, f):
        self.workers.append(make_thread(f, daemon=True))

    def run(self):
        self.now = 0
        self.phase = 'init'
        [self.worker(run) for run in runs(self.entities)]
        start_threads(self.actors)

        self.phase = 'before init'
        self.before_init()
        self.step(self.actors)
        self.phase = 'after init'
        self.after_init()

        start_threads(self.workers)
        for self.now in itertools.count():

            self.phase = 'before worker output'
            self.before_worker_output()
            self.step(self.workers)
            self.phase = 'after worker output'
            self.after_worker_output()

            self.phase = 'before transfer'
            self.before_transfer()
            [p.transfer() for p in self.ports]
            self.phase = 'after transfer'
            self.after_transfer()

            self.phase = 'before worker input'
            self.before_worker_input()
            self.step(self.workers)
            self.phase = 'after worker input'
            self.after_worker_input()

            self.now += 1
            self.phase = 'before actor'
            self.before_actor()
            self.step(self.actors)
            self.phase = 'after actor'
            self.after_actor()

            if not self.actors:
                break

    def step(self, threads):
        wait_threads(threads)

    def title(self):
        utils.put('=' * 25 + ' {} {}'.format(self.now, self.phase))

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

def start_threads(ts):
    [t.start() for t in ts]

def wait_threads(ts):
    [t.inform.put(1) for t in ts]
    ts[:] = [t for t in ts if t.report.get()]

network = Network()
