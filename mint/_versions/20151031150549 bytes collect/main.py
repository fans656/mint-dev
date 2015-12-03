'''
         0x 01 02
pc1 send 0000 0001 0000 0002
pc2 recv 0000 0000 0010 0000 0100 0000
         0x 00 20 40
         first 3 bits is noise preamble
         so the 0x01 02 became received as 00 20 40
'''
import mint
from mint.components import Link

from devices import PC

def monitor(net):
    return
    print 'Now is {}'.format(net.env.now)
    print '{:1} -> {:<28} {:>2} >-> {:<2} {:>28} -> {:1}'.format(
            pc1.name, ''.join(list(reversed(pc1.port.obuffer))), ''.join(list(reversed(link.ports[0].ibuffer))),
            ''.join(list(reversed(link.ports[1].obuffer))), ''.join(list(reversed(pc2.port.ibuffer))), pc2.name
            )
    print '{:1} <- {:<28} {:>2} <-< {:<2} {:>28} <- {:1}'.format(
            pc1.name, pc1.port.ibuffer, link.ports[0].obuffer,
            link.ports[1].ibuffer, pc2.port.obuffer, pc2.name
            )
    raw_input()
    #import code
    #code.interact(local=globals())

@mint.proc()
def sender():
    pc1.port.put('\x01\x02')
    yield mint.end

@mint.proc()
def receiver():
    #print 'Received:', pc2.recv(2)
    yield mint.end

pc1 = PC('a')
pc2 = PC('b')
link = Link(pc1, pc2)
mint.run(monitor=monitor)
