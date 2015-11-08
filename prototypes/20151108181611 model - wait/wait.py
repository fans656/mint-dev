import threading
import Queue
import itertools
import sys

class Network(object):

    def __init__(self):
        self.actors = []
        self.workers = []

    def actor(self, f):
        self.actors.append(make_thread(f))

    def worker(self, f):
        self.workers.append(make_thread(f))

    def title(self, phase=''):
        self.phase = phase
        put('=' * 25, self.now, self.phase)

    def run(self):
        self.now = 0
        start_threads(self.actors)
        self.title('initial (actor)')
        wait_threads(self.actors)
        start_threads(self.workers)
        for self.now in itertools.count():
            self.title('worker')
            wait_threads(self.workers)
            self.title('transfer')
            # self.transfer()
            raw_input('...')
            self.now += 1
            self.title('actor')
            wait_threads(self.actors)

def wait(n_steps=1):
    t = threading.current_thread()
    n_switches = n_steps + 1 if n_steps else 1
    for _ in xrange(n_switches):
        t.report.put(1)
        t.inform.get()

def make_thread(f):

    def f_():
        t = threading.current_thread()
        t.inform.get()
        f()
        t.report.put(0)

    t = threading.Thread(target=f_)
    t.inform = Queue.Queue()
    t.report = Queue.Queue()
    return t

def start_threads(threads):
    [t.start() for t in threads]

def wait_threads(threads):
    [t.inform.put(1) for t in threads]
    threads[:] = [t for t in threads if t.report.get()]

def put(s, *args, **kwargs):
    if isinstance(s, str) and '{' in s:
        if args or kwargs:
            s = s.format(*args, **kwargs)
    else:
        s = ' '.join(map(str, [s] + list(args)))
    sys.stdout.write(s + '\n')

def f():
    put('hi')
    wait(2)
    put('me')
    wait(2)
    put('you')

def g():
    wait(0)
    put('g hi')
    wait(0)
    put('g me')
    wait(0)
    put('g you')

def h():
    while True:
        put('worker')
        wait(0)

net = Network()
net.actor(f)
net.actor(g)
net.worker(h)
net.run()
