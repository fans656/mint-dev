'''
arp

without knowing b's mac, a perform arp first.
try uncomment `a.arp_table[b.ip] = b.mac`,
then a will send packet directly.
but with switch not knowing b's mac-port by the respond arp packet,
this will result flood so b and c both receives the packet.
'''
from mint import *
from mint.pdus import Packet

a, b, c = Host(), Host(), Host()
#a.arp_table[b.ip] = b.mac
s = Switch()
link(a, s.tips[0])
link(b, s.tips[1])
link(c, s.tips[2])

@actor
def _():
    a.send('hi', ip='1.0.0.2')

run(gui=True, until=999)
