'''
frame oversize lost

a and b both sends to c.
with a sending frame with 1-byte payload (thus 3-byte frame);
with b sending frame with 7-byte payload (thus 9-byte frame),
which can't fit in switch's port-2 obuffer, thus all lost for c.
'''
import struct
from mint import *

a, b, c = Host(), Host(), Host()
s = Switch()
s.ports[2].obuffer.size = 8
link(a, s.tips[0])
link(b, s.tips[1])
link(c, s.tips[2])

n = 2
def send(sender, size):
    for i in range(n):
        data = '\x00' * (size - 1) + struct.pack('!B', i + 1)
        sender.send(data, c.mac)
actor(send, a, 1)
actor(send, b, 7)

run(gui=True, until=265)
