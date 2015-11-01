import sys
import functools

class Stop(Exception): pass

def refresh():
    global network, env
    from mint.network import Network
    network = Network()
    env = network.env

def proc(*args, **kws):
    global network
    def deco(f):
        network.env.process(f(*args, **kws))
    return deco

def run(*args, **kwargs):
    network.run(*args, **kwargs)

def block(f):
    @functools.wraps(f)
    def f_(*args, **kwargs):
        return env.process(f(*args, **kwargs))
    return f_

def setup(f):
    @functools.wraps(f)
    def f_(*args, **kwargs):
        refresh()
        ret = f(*args, **kwargs)
        try:
            run()
        except Stop:
            pass
        return ret
    return f_

def ret(val):
    env.exit(val)

network = None
env = None
refresh()
end = network.env.event()
end.succeed()
