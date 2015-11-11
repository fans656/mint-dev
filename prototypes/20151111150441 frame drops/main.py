'''
a send 3 frames
b wait 48 laps before recv
it lose the second frame ('\x01')

actor in the 48th lap still do nothing, it `recv` in the 49th lap
so when nic got the second frame (lap-48) and want to put it in the ibuffer
there are no enough room, so it drop the frame
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
    wait(48)
    print repr(b.nic.recv())
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
