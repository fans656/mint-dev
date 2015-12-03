import functools
import threading

from mint import network
from mint.utils import put, bitify, unbitify, format, view_queue

def refresh():
    network.network = network.Network()

def actor(*fs, **kwargs):
    if all(hasattr(f, '__call__') for f in fs):
        network.network.actor(*fs)
    else:
        f, args = fs[0], fs[1:]
        f = functools.partial(f, *args, **kwargs)
        network.network.actor(f)

def debug(f):
    network.network.debug_params = f

def now():
    return network.network.now

def title():
    network.network.title()

def run(*args, **kwargs):
    network.network.run(*args, **kwargs)

def pause():
    raw_input()

def wait(n_steps=1):
    t = threading.current_thread()
    n_switches = n_steps + 1 if n_steps else 1
    for _ in range(n_switches):
        t.report.put(1)
        t.inform.get()

def timer(*args, **kwargs):
    return network.network.timer(*args, **kwargs)

def kill(*args, **kwargs):
    return network.network.kill(*args, **kwargs)

def link(*args, **kwargs):
    return Link(*args, **kwargs)

def setup(f):
    f._mint_data = utils.Bunch(type='setup')
    return f

def output(f):
    f._mint_data = utils.Bunch(type='output')
    return f

def input(f):
    f._mint_data = utils.Bunch(type='input')
    return f

def _gen_decorator(name):
    def deco(priority):
        def deco_(f):
            f._mint_data = utils.Bunch(type=name, priority=priority)
            return f
        if callable(priority):
            f = priority
            return deco_(f)
        else:
            return deco_
    deco.func_name = name
    return deco

sender = _gen_decorator('sender')
recver = _gen_decorator('recver')

def debug(f):
    network.network.debug = f

from mint.devices import Host, Hub
from mint.links import Link
from mint.protocols import Protocol
