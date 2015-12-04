'''
look the b's arp response! which got the dst_ip == 127.0.0.1

switch cares about nothing above layer-2
and since arp packet is directly built upon layer-2 frame
it will happily travel in a switched network with those invalid
LOOPBACK ip address
'''
from mint import *
from mint.pdus import Packet

a, b, c = Host(), Host(), Host()
a.ip = '127.0.0.1'
#a.arp_table[b.ip] = b.mac
s = Switch()
link(a, s.tips[0])
link(b, s.tips[1])
link(c, s.tips[2])

@actor
def _():
    a.send('hi', ip='1.0.0.2')

run(gui=True, until=999)
