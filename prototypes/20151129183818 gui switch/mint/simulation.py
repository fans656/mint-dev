import sys, os, functools
import timpy
import mint
import utils
from collections import defaultdict
from utils import each

ACTOR_PRIORITY = 999
WORKER_PRIORITY = 0
SWITCH_PRIORITY = -1
LINK_PRIORITY = -999

class Simulation(object):

    current_sim = None

    def __init__(self):
        self.env = timpy.Environment()
        self.entities = []
        self.indexes = defaultdict(lambda: 0)
        self.gui_running = False
        self.gui_stdout = []
        Simulation.current_sim = self
        # step by constants
        self.Phase = self.env.Priority
        self.TikTok = self.env.Time
        self.Action = self.env.Thread

    def banner(self, role=''):
        utils.put('=' * 20, self.now, role)

    def add(self, o):
        cls = type(o)
        o.index = self.indexes[cls]
        self.indexes[cls] += 1
        self.entities.append(o)

    def actor(self, f):
        return self.env.process(f, priority=ACTOR_PRIORITY)

    def worker(self, f, **kwargs):
        return self.env.process(f, daemon=True, **kwargs)

    def process(self, *args, **kwargs):
        return self.env.process(*args, **kwargs)

    def elapse(self, time):
        self.env.timeout(time)

    def put(self, *args, **kwargs):
        if self.gui_running:
            s = utils.put_format(*args, **kwargs)
            self.gui_stdout.append(s)
        else:
            return utils.put(*args, **kwargs)

    @property
    def now(self):
        return self.env.now

    @property
    def status(self):
        if not self.started:
            return 'Initial'
        if not self.finished:
            return 'Running'
        return 'Finished'

    @property
    def finished(self):
        return self.env.finished

    @property
    def started(self):
        return self.env.started

    @property
    def stdout(self):
        return self.gui_stdout

    def run(self, until=None, gui=False, *args, **kwargs):
        if until is not None:
            self.actor(lambda: self.elapse(until))
        if gui:
            self.gui_running = True
            from gui import run
            run(self)
        else:
            while not self.env.finished:
                self.step(*args, **kwargs)

    def step(self, before=None, after=None, role='', **kwargs):
        del self.gui_stdout[:]
        if before:
            self.banner(role)
            before()
            raw_input()
        self.env.step(**kwargs)
        if after:
            self.banner(role)
            after()
            raw_input()

sim = Simulation()
