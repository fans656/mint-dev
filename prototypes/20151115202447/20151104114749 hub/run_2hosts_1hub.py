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
h = Hub()
link(a, h.ports[0])
link(h.ports[1], b)

data = '1'

run()
