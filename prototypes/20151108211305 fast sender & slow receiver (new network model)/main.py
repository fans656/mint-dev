'''
fast sender & slow receiver
b wait 63 tik-toks before begin recv
this will cause all but the first frame be dropped
due to insufficient `iframes` room
'''
import mint
from mint import *

@actor
def _():
    for i in range(1, 8+1):
        data = chr(i << 1)
        a.nic.send(data)

@actor
def _():
    wait(63)
    #put(b.nic.iframes)
    #put(b.nic.iframe)
    for _ in range(8):
        data = b.nic.recv()
        put('{:4} {}', now(), repr(data))

#@after_worker
def _():
    title()
    put(view_queue(a.nic.oframes))
    put(a.nic.oframe)
    a.port.show()
    l.ports[0].show()
    l.ports[1].show()
    b.port.show()
    put(b.nic.iframe)
    put(view_queue(b.nic.iframes))
    raw_input()

a, b = Host(), Host()
l = link(a, b)
b.nic.set_max_n_frames(1)
run()
