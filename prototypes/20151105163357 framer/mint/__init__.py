import functools

from mint import network
from mint.components import Link, Host, Hub
from mint.utils import put, bitify, unbitify, format

def refresh():
    network.network = network.Network()

def proc(*fs, **kwargs):
    if all(hasattr(f, '__call__') for f in fs):
        network.network.proc(*fs)
    else:
        f, args = fs[0], fs[1:]
        f = functools.partial(f, *args, **kwargs)
        network.network.proc(f)

def now():
    return network.network.now

def phase():
    return network.network.phase

def run(*args, **kwargs):
    network.network.run(*args, **kwargs)

def stopped():
    return network.network.stopped

def wait(*args, **kwargs):
    network.network.wait(*args, **kwargs)

def link(*args, **kwargs):
    return Link(*args, **kwargs)
