from mint import network

def refresh():
    network.network = Network()

def proc(f):
    network.network.add_thread(f)

run = network.network.run
env = network.network.env
