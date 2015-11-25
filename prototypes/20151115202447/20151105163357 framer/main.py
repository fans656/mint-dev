'''
1 hub connects 3 hosts.
a and b send simultaneously, so c will receive garbage.
In fact, it's unable to discover that a frame has been sent.
So we use c.port.recv(..) here.
If we'd use c.recv(), it will hang forever.
a and b can receive each other's message correctly.

Interestingly, if we increse the latency of b-hub link,
the message c received will change accordingly.
Try increese the latency to, say, 95 - see what happens? Why?
'''
from mint import *
from devices import PC

@proc
def _():
    a.send('hello world')
    b.send('who are you')
    put(a, repr(a.recv(11)), now())

@proc
def _():
    put(b, repr(b.recv(11)), now())

@proc
def _():
    d = c.port.recv(3 + 8 + 11 * 8)
    d = utils.unbitify(d[3 + 8:])
    put(c, repr(d), now())

a, b, c = PC('a'), PC('b'), PC('c')
hub = Hub()
link(a, hub.ports[0])
link(b, hub.ports[1], latency=0)
link(c, hub.ports[2])

run()
