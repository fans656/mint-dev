'''
3 host, 1 switch
a, b, c each has mac address 0x01, 0x02, 0x03

a sends '\xff' to b.
without previous knowledge on which host on which port,
the switch flood this frame to both port-1(b) and port-2(c).
since it detected incoming frame from a on port-0,
it register this fact in its route table.

at time 50, b sends '\x81' to a.
the switch finds in its route table that a is on port-0,
so it only send this frame('\x81') out by port-0(a).
also it register b's mac(0x02) with port-1.

at time 141, the switch's entry duration is dued,
it cleans up a's entry (0x01: [0]).
note that b's entry is not expired so not cleaned.

at time 190, b's entry is also expired, thus cleaned.

at time 200, a sends another frame('\xfe') to b.
becuase there are no entries for b in the switch anymore,
this frame is again flooding to both b and c.

b and c received the frame at time 283.
'''
import struct
from mint import *

@actor
def _():
    a.send('\xff', b.mac)
    elapse(200)
    a.send('\xfe', b.mac)

@actor
def _():
    elapse(50)
    b.send('\x81', a.mac)

a, b, c = Host(), Host(), Host()
switch = Switch()
link(a, switch.tips[0])
link(b, switch.tips[1])
link(c, switch.tips[2])

run(gui=True, until=400)
