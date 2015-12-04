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
    #a.send('hi')
    #a.send('hi', mac=0x02)
    a.send('hi', ip='1.0.0.2')

run(gui=True, until=2571)
