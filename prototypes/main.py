import mint
from mint import *

@actor
def _():
    a.nic.send('\xff')

@actor
def _():
    put('{:6} {}', now(), format(b.nic.recv(), 'bin'))

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
l = link(a, b, latency=8)
b.nic.set_max_n_frames(1)
run()
