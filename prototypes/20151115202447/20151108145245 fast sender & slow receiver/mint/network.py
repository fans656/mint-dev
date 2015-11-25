import threading
import itertools
import Queue
from collections import defaultdict

from mint import utils

debug_params = {}

class Network(object):

    class Stopped(Exception): pass

    def __init__(self):
        self.entities = []
        self.ports = []
        self.threads = []
        self.names = defaultdict(lambda: -1)
        self.stopped = False
        self.debug_params = {}

    def new_name(self, entity):
        cls = entity.__class__
        self.names[cls] += 1
        return self.names[cls]

    def add(self, *entities):
        self.entities.extend(entities)
        self.ports.extend(port
                for entity in entities
                for port in entity.ports)

    def actor(self, *fs, **kwargs):
        daemon = kwargs.get('daemon', False)
        self.threads.extend(wrap(f, daemon) for f in fs)

    def run(self):
        self.debug_setup()
        self.now = 0
        self.phase = 'initial'
        for e in filter(lambda e: hasattr(e, 'run'), self.entities):
            self.actor(e.run, daemon=True)
        actors, workers = [], []
        for thread in self.threads:
            (workers if thread.daemon else actors).append(thread)
        for actor in actors:
            actor.start()
        actors = self.tik(actors, 'initial')
        for worker in workers:
            worker.start()
        for self.now in self.tik_toks():
            workers = self.tik(workers, 'output')
            actors = self.tik(actors, 'output')
            self.tok() # core transfer
            workers = self.tik(workers, 'input')
            actors = self.tik(actors, 'input')
            if not actors and not self.debug_func:
                break

    def tik_toks(self):
        return itertools.count()

    def tik(self, threads, phase):
        # let user threads go
        for t in threads:
            t.inform.put(1)
        # wait user threads pause
        threads = [t for t in threads if t.is_alive()]
        t_threads = []
        for t in threads:
            alive = t.report.get()
            if alive:
                t_threads.append(t)
        self.call_debug_func(phase)
        return t_threads

    def tok(self):
        for port in self.ports:
            port.transfer()
        self.call_debug_func('transfer')

    def wait(self, n_steps=1):
        t = threading.current_thread()
        n_steps += 1
        for _ in range(n_steps):
            t.report.put(1)
            t.inform.get()

    def debug_setup(self):
        debug_params = self.debug_params
        if hasattr(debug_params, '__call__'):
            debug_params = {'func': debug_params}
        self.debug_phases = debug_params.get('phases', ['all'])
        self.debug_func = debug_params.get('func', None)
        if 'all' in self.debug_phases:
            self.debug_phases = ('initial', 'output', 'input', 'transfer')

    def call_debug_func(self, phase):
        self.phase = phase
        if self.debug_func and phase in self.debug_phases:
            self.debug_func()

    def title(self):
        utils.put('=' * 25 + ' {} {}'.format(self.now, self.phase))

def runs(entities):
    return (wrap(e.run) for e in entities if hasattr(e, 'run'))

def wrap(f, daemon):
    def f_(*args, **kwargs):
        t = threading.current_thread()
        try:
            t.inform.get()
            f(*args, **kwargs)
        finally:
            t.report.put(0)
    return register_func(f_, daemon)

def register_func(f, daemon):
    thread = threading.Thread(target=f)
    return register(thread, daemon)

def register(thread, daemon=False):
    thread.daemon = daemon
    thread.inform = Queue.Queue()
    thread.report = Queue.Queue()
    thread.registered = True
    return thread

def registered(thread):
    try:
        return thread.registered
    except AttributeError:
        return False

network = Network()
