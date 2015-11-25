import sys, os, functools
import timpy
import mint
import utils
from collections import defaultdict
from utils import each

ACTOR_PRIORITY = 999
NIC_PRIORITY = 1
LINK_PRIORITY = 0

class Simulation(object):

    current_sim = None

    def __init__(self):
        self.env = timpy.Environment()
        self.entities = []
        self.started = False
        self.indexes = defaultdict(lambda: 0)
        self.gui_running = False
        Simulation.current_sim = self
        # step by constants
        self.Priority = self.env.Priority
        self.Time = self.env.Time
        self.Thread = self.env.Thread

    def banner(self, role=''):
        utils.put('=' * 20, self.now, role)

    def add(self, o):
        cls = type(o)
        o.index = self.indexes[cls]
        self.indexes[cls] += 1
        self.entities.append(o)

    def actor(self, f):
        return self.env.process(f, priority=ACTOR_PRIORITY)

    def process(self, *args, **kwargs):
        return self.env.process(*args, **kwargs)

    def elapse(self, time):
        self.env.timeout(time)

    @property
    def now(self):
        return self.env.now

    @property
    def finished(self):
        return self.env.finished

    def run(self, gui=False, **kwargs):
        if gui:
            import gui
            gui.run(self)
        else:
            while not self.env.finished:
                self.step(*args, **kwargs)

    def step(self, before=None, after=None, role='', **kwargs):
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
