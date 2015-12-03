'''
fast sender & slow receiver
when b process the frame too long (e.g. wait(30) after recv the frame)
it will lose some frames

note b set the buffer size so it can hold 1 frame at most
if it has the same buffer which can hold 8 frames as a does
all the frames is received ok
'''
import Queue

from mint import *
from mint.core import Entity

@actor
def _():
    for i in range(8):
        data = chr((i + 1) << 1)
        a.send(data)

@actor
def _():
    for _ in range(8):
        data = repr(b.nic.recv())
        put('recv {:4} {}', now(), data)
        wait(30)

a, b = Host(), Host()
b.nic.set_max_n_frames(1)
link(a, b)
run()
