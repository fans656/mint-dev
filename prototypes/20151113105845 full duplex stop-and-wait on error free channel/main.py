'''
full duplex stop and wait on error free channel

see devices.py for the protocol implementation
'''
import mint
import struct

import mint
from mint import *

from devices import PC

@actor
def _():
    for i in xrange(32):
        a.send(struct.pack('!B', i))

@actor
def _():
    for i in xrange(32):
        put(struct.unpack('!B', b.recv())[0])

a, b = PC(), PC()
l = link(a, b)
run()
