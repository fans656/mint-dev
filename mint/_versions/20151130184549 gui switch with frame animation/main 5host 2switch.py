import struct
from mint import *

@actor
def _():
    a.send('\x01', b.mac)
    elapse(170)
    a.send('\x02', b.mac)

@actor
def _():
    elapse(90)
    b.send('\x10', a.mac)

a, b, c = Host(), Host(), Host()
d, e = Host(), Host()
s1, s2 = Switch(n_tips=4), Switch()

link(a, s1.tips[0])
link(b, s1.tips[1])
link(c, s1.tips[2])

link(d, s2.tips[0])
link(e, s2.tips[1])

link(s1.tips[3], s2.tips[2])

run(gui=True, until=400)
