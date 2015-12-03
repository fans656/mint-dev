from mint import *

@proc
def _():
    a.port.send(data)

@proc
def receiver():
    entity = b
    data = entity.port.recv(8)
    print '{} received {} at {}\n'.format(entity, data, now())
    stop()

a, b = (Host() for _ in range(2))
h1, h2 = (Hub() for _ in range(2))
link(a, h1.ports[0])
link(h1.ports[1], h2.ports[0])
link(h2.ports[1], b)

data = '1'

run()
