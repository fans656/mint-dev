import struct
from mint import *

@actor
def _():
    a.send('\xff', b.mac)
    elapse(200)
    a.send('\xfe', b.mac)

@actor
def _():
    elapse(80)
    b.send('\x81', a.mac)

a, b, c = Host(), Host(), Host()
switch = Switch()
link(a, switch.tips[0])
link(b, switch.tips[1])
link(c, switch.tips[2])

run(gui=True, until=400)
