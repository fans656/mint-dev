'''
    pc1 send 11111 to pc2
    pc2 send 11 to pc1 1 second later
    the dot is configured as noise bit
'''
from devices import PC
import mint
from mint import Link

pc1 = PC('fans656')
pc2 = PC('twiispa')
link = Link(pc1, pc2)

def monitor(net):
    print 'Now is {}'.format(net.env.now)
    print '{:7} -> {:<11}  {:>11} >-> {:<11}  {:>11} -> {:7}'.format(
            pc1.name, ''.join(list(reversed(pc1.port.obuffer))), ''.join(list(reversed(link.ports[0].ibuffer))),
            ''.join(list(reversed(link.ports[1].obuffer))), ''.join(list(reversed(pc2.port.ibuffer))), pc2.name
            )
    print '{:7} <- {:<11}  {:>11} <-< {:<11}  {:>11} <- {:7}'.format(
            pc1.name, pc1.port.ibuffer, link.ports[0].obuffer,
            link.ports[1].ibuffer, pc2.port.obuffer, pc2.name
            )
    raw_input()
    #import time
    #time.sleep(0.8)

#@mint.proc
def sender():
    pc1.port.put('11111', True)
    yield env.timeout(1)
    pc2.port.put('11', True)
    yield end

Link.noise_bit = lambda self: '.'

#link.latency = 1
net = mint.network
env = net.env
end = env.event()
end.succeed()
env.process(sender())
net.run(monitor=monitor)
