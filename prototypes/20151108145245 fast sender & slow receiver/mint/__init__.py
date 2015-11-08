import functools

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

def stopped():
    return network.network.stopped

def wait(*args, **kwargs):
    network.network.wait(*args, **kwargs)

def link(*args, **kwargs):
    return Link(*args, **kwargs)
