'''
threaded version simpy
entity and port as real thread

a sends 111
b sends 10101
latency == 3
b recv 000111
a recv 00010101
'''
import time
import mint
from mint.components import Endpoint, Link

a = Endpoint('a')
b = Endpoint('b')
link = Link(a, b)

a_data = '111'
b_data = '10101'
latency = 3
link.latency = latency

@mint.proc
def sender():
    a.port.send(a_data)
    print '{} recv: {}'.format(a, a.port.recv(len(b_data) + latency))
    print 'now is {}'.format(mint.env.now)

@mint.proc
def receiver():
    b.port.send(b_data)
    print '{} recv: {}'.format(b, b.port.recv(len(a_data) + latency))
    print 'now is {}'.format(mint.env.now)

mint.run()
