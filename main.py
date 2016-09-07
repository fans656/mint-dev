from mint import *
from mint.protocols.test import Retransmit

a, b, c = Host(), Host(), Host()
s = Switch()

link(a, s.tips[0], 1)
link(b, s.tips[1], 2)
#link(c, s.tips[2], 3)

a += Retransmit()

a.send('hi')
#b.send('me').at(5)

start()
