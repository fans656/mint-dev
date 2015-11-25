import functools
import threading

from mint import network
from mint.devices import Host, Hub
from mint.links import Link
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

def phase():
    return network.network.phase

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

def link(*args, **kwargs):
    return Link(*args, **kwargs)

def before_init(f):
    network.network.before_init = f

def after_init(f):
    network.network.after_init = f

def before_worker(f):
    network.network.before_worker = f

def after_worker(f):
    network.network.after_worker = f

def before_transfer(f):
    network.network.before_transfer = f

def after_transfer(f):
    network.network.after_transfer = f

def before_actor(f):
    network.network.before_actor = f

def after_actor(f):
    network.network.after_actor = f

def debug(f):
    network.network.before_init = f
    network.network.after_init = f
    network.network.before_worker = f
    network.network.after_worker = f
    network.network.before_transfer = f
    network.network.after_transfer = f
    network.network.before_actor = f
    network.network.after_actor = f

def debug_after(f):
    network.network.after_init = f
    network.network.after_worker = f
    network.network.after_transfer = f
    network.network.after_actor = f
