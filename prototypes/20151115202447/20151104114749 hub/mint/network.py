import threading
import itertools
import Queue
from collections import defaultdict

from mint import utils

class Network(object):

    def __init__(self):
        self.entities = []
        self.ports = []
        self.threads = []
        self.thread_queues = {}
        self.before_step_func = lambda: None
        self.after_step_func = lambda: None
        self.names = defaultdict(lambda: -1)
        self.informing_queue = Queue.Queue()
        self.reporting_queue = Queue.Queue()
        self.stopped = False
        self.now = 0

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
        self.threads.extend(threading.Thread(target=self.wrap(f))
                for f in fs)

    def wrap(self, f):
        def f_(*args, **kwargs):
            ret = f(*args, **kwargs)
            self.finish()
            return ret
        return f_

    def run(self):
        # add entity.run as thread
        self.proc(*(entity.run
                for entity in self.entities
                if hasattr(entity, 'run')))
        # make thread sync queues
        self.thread_queues = dict(zip(self.threads,
            (utils.Bunch(inform=Queue.Queue(), report=Queue.Queue())
            for _ in itertools.count())))
        # start threads
        for thread in self.threads:
            thread.start()

        def show_ports(msg=''):
            print '=' * 20 + '{}: {}'.format(self.now, msg)
            for port in self.ports:
                port.show()
            raw_input()
        # main loop
        while True:
            # wait for threads to block
            threads = []
            for thread in self.threads:
                status = self.thread_queues[thread].report.get()
                if status == 'stop':
                    self.stopped = True
                if status != 'finish':
                    threads.append(thread)
            self.threads = threads
            #show_ports('entity stepped')
            # world step
            self.before_step_func()
            for port in self.ports:
                port.pull()
            #show_ports('pulled')
            for port in self.ports:
                port.output()
            #show_ports('outputed')
            for port in self.ports:
                port.input()
            #show_ports('inputed')
            for port in self.ports:
                port.push()
            self.now += 1
            self.after_step_func()
            # let go of threads
            for thread in self.threads:
                qs = self.thread_queues[thread]
                qs.inform.put('continue')
            if self.stopped:
                break

    def stop(self):
        thread = threading.current_thread()
        qs = self.thread_queues[thread]
        qs.report.put('stop')

    def wait(self, n_steps=1):
        thread = threading.current_thread()
        qs = self.thread_queues[thread]
        for _ in range(n_steps + 1):
            qs.report.put('continue')
            qs.inform.get()

    def finish(self):
        thread = threading.current_thread()
        qs = self.thread_queues[thread]
        qs.report.put('finish')

    def before_step(self, f):
        self.before_step_func = f
        return f

    def after_step(self, f):
        self.after_step_func = f
        return f

network = Network()
