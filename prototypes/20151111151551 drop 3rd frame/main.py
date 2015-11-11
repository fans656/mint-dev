'''
lose the 3rd frame

b `recv` at 24lap
then `wait` 47laps, at the 23 + 1 + 47 + 1 == 72lap
nic got the 3rd frame, but the 2nd frame is still in the buffer
which is about to `recv` by OS later in the same lap
so the 3rd frame is dropped

Note that `wait(2)` is not equivalent to two successive `wait(1)`
because the two `wait(1)` composed to a 3lap duration!

    wait(1)
    # do nothing
    wait(1)

you can view it this way

    wait(2)

is equivalent to

    wait(0)
    wait(0)
    wait(0)

while

    wait(1)
    # do nothing
    wait(1)

is equivalent to

    wait(0)
    wait(0)
    # do nothing
    wait(0)
    wait(0)

'''
import mint
from mint import *

@actor
def _():
    a.nic.send('\x00')
    a.nic.send('\x01')
    a.nic.send('\x02')

@actor
def _():
    wait(23)
    print repr(b.nic.recv())
    wait(47)
    print repr(b.nic.recv())
    print repr(b.nic.recv())

#@after_worker_input
def _():
    title()
    put(a.nic._oframes)
    put(a.nic._oframe)
    a.port.show()
    l.ports[0].show()
    l.ports[1].show()
    b.port.show()
    put('isymbol: {}', b.nic.port.isymbol)
    put(b.nic._iframe)
    put(b.nic._iframes)
    raw_input()

a, b = Host(), Host()
b.nic.buffer_size = 1
l = link(a, b)
run()
