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
        self.procs = []
        self.names = defaultdict(lambda: -1)
        self.stopped = False

    def new_name(self, entity):
        cls = entity.__class__
        self.names[cls] += 1
        return self.names[cls]

    def add(self, *entities):
        self.entities.extend(entities)
        self.ports.extend(port
                for entity in entities
                for port in entity.ports)

    def proc(self, *fs):
        self.procs.extend(wrap(f) for f in fs)

    def run(self, until=None, debug={}):
        self.now = 0
        self.setup_debug(debug)
        self.start_entities()
        for self.now in self.tik_toks(until):
            self.tik()
            self.tok()
            if self.stopped:
                self.shutdown()
                break
        else:
            self.stopped = True
            self.shutdown()

    def tik_toks(self, until):
        return xrange(until) if until else itertools.count()

    def start_entities(self):
        self.threads = gen_threads(self.procs, daemon=False)
        self.threads += gen_threads(runs(self.entities), daemon=True)
        for thread in self.threads:
            thread.start()

    def tik(self):
        for t in self.threads:
            t.inform.put(1)
        threads = []
        proc_threads = []
        for t in self.threads:
            if t.report.get():
                threads.append(t)
            if not t.daemon:
                proc_threads.append(t)
        self.threads = threads
        if not proc_threads:
            self.stopped = True
        self.call_debug_func('tiked')

    def tok(self):
        for port in self.ports:
            port.pull()
        self.call_debug_func('pulled')
        for port in self.ports:
            port.output()
        self.call_debug_func('outputted')
        for port in self.ports:
            port.input()
        self.call_debug_func('inputted')
        for port in self.ports:
            port.push()
        self.call_debug_func('pushed')

    def shutdown(self):
        for t in self.threads:
            t.inform.put(0)
        for t in self.threads:
            t.join()

    def wait(self, n_steps=1):
        if self.stopped:
            raise Network.Stopped()
        t = threading.current_thread()
        for _ in range(n_steps + 1):
            t.report.put(1)
            t.inform.get()

    def setup_debug(self, debug_params):
        if hasattr(debug_params, '__call__'):
            debug_params = {'func': debug_params}
        self.debug_phases = debug_params.get('phases', ['all'])
        self.debug_func = debug_params.get('func', lambda: None)
        if 'all' in self.debug_phases:
            self.debug_phases = ('tiked', 'pulled', 'outputted', 'inputted', 'pushed')

    def call_debug_func(self, phase):
        self.phase = phase
        if phase in self.debug_phases:
            self.debug_func()

def runs(entities):
    return (wrap(e.run) for e in entities if hasattr(e, 'run'))

def gen_threads(fs, daemon):
    threads = []
    for f in fs:
        thread = threading.Thread(target=f)
        thread.daemon = daemon
        thread.inform = Queue.Queue()
        thread.report = Queue.Queue()
        threads.append(thread)
    return threads

def wrap(f):
    def f_(*args, **kwargs):
        t = threading.current_thread()
        try:
            t.inform.get()
            ret = f(*args, **kwargs)
            t.report.put(0)
            return ret
        except Network.Stopped:
            pass
    return f_

network = Network()
