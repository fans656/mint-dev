'''
use Protocol (inherited from Entity) to model protocols

see protocols.py
'''
import mint
import struct

import mint
from mint import *

from devices import PC

n = 16

@actor
def _():
    a.send('hi')
    put(a.recv())

@actor
def _():
    put(b.recv())
    b.send('hi, how are you?')

a, b = PC(), PC()
l = link(a, b)

#@a.top.debug
#@b.top.debug
def _(header, payload, tail,
        host=None, protocol=None, type=None, **_):
    title()
    put(host, type)
    put(protocol.unbuild(header))
    put(repr(header), repr(payload))
    put(host, 's:', protocol.sending_seq,
            'e:', protocol.expecting_seq)
    #put(a.top._seq)
    pause()

run()
