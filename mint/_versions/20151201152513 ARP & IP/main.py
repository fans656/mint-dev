'''
ARP & IP

3 host, 1 switch

a wants to send 'hi' to b, due to not knowing it's MAC address,
a sends an ARP query first - by a ARP.WhoIs packet.
b and c both received the query,
but only b answers it - by a ARP.IAm packet.
a received the ARP.IAm, then sends the pending packet to b.
b received it.

you may want to check the `opdu` and `ipdu` tab on the relevent hosts' console
'''
import struct
from mint import *

a, b, c = Host(), Host(), Host()
s = Switch()
link(a, s.tips[0])
link(b, s.tips[1])
link(c, s.tips[2])

@actor
def _():
    a.l3send('hi', b.ip)

run(gui=True, until=775)
