'''
frame lost caused by switch port congestion - multiple sender one receiver

a and b both sends 3 frames ('\x01', '\x02', \x03) to c.
due to c is silent all the time, switch has to flood all these frames.
so a received b's frames for c, all of them;
   b received a's frames for c, all of them.
but c only received 4 frames, which are:
    '\x01' from a to c
    '\x01' from b to c
    '\x02' from a to c
    '\x03' from a to c
the '\x02', '\x03' from b to c is lost.
why? because switch's port-2 has only a 8-bytes obuffer.
so it contains at most 2 frames at a time
(assuming 1-byte payload and 2-byte addresses).

this lost is caused by multiple sender one receiver congestion,
and has to be dealt by upper layer protocols.
'''
import struct
from mint import *

a, b, c = Host(), Host(), Host()
s = Switch()
s.ports[2].obuffer.size = 8
link(a, s.tips[0])
link(b, s.tips[1])
link(c, s.tips[2])

n = 3
def send(sender):
    for i in range(n):
        sender.send(struct.pack('!B', i + 1), c.mac)
actor(send, a)
actor(send, b)

run(gui=True, until=201)
