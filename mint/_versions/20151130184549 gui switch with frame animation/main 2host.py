import struct
from mint import *

@actor
def _():
    a.send('\xff', b.mac)
    elapse(5)
    b.send('\xff', a.mac)

a, b = Host(), Host()
link(a, b)

run(gui=True, until=46)
