import sys

__ALL__ = ['refresh', 'proc', 'run', 'network', 'end']

def refresh():
    global network
    from mint.network import Network
    network = Network()

def proc(*args, **kws):
    global network
    def deco(f):
        network.env.process(f(*args, **kws))
    return deco

def run(*args, **kwargs):
    network.run(*args, **kwargs)

network = None
refresh()
end = network.env.event()
end.succeed()
