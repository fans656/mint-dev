from mint import network
from mint.components import Link, Host

def refresh():
    network.network = Network()

def proc(*fs):
    network.network.proc(*fs)

def now():
    return network.network.now

def run():
    network.network.run()

def stop():
    network.network.stop()

def wait(*args, **kwargs):
    network.network.wait(*args, **kwargs)

def before_step():
    network.network.before_step()

def after_step():
    network.network.after_step()
