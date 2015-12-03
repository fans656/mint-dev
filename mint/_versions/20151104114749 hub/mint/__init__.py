import functools

from mint import network
from mint.components import Link, Host, Hub

def refresh():
    network.network = Network()

def proc(*fs, **kwargs):
    if all(hasattr(f, '__call__') for f in fs):
        network.network.proc(*fs)
    else:
        f, args = fs[0], fs[1:]
        f = functools.partial(f, *args, **kwargs)
        network.network.proc(f)

def now():
    return network.network.now

def run():
    network.network.run()

def stop():
    network.network.stop()

def stopped():
    return network.network.stopped

def wait(*args, **kwargs):
    network.network.wait(*args, **kwargs)

def before_step():
    network.network.before_step()

def after_step():
    network.network.after_step()

def link(*args, **kwargs):
    return Link(*args, **kwargs)
