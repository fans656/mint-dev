'''
a sends 'hi', b lost it (1st)
a resends 'hi', b lost it (2nd)
a resends 'hi', b lost it (3rd)
a resends 'hi', b got it
b acknowledges, a lost it (1st)
a resends 'hi', b got it
b acknowledges, a got it
a sends 'how are you?', b got it
'''
from mint import *
from devices import PC

@actor
def _():
    a.send('hi')
    a.send('how are you?')

@actor
def _():
    put(b, 'recved', repr(b.recv()))
    put(b, 'recved', repr(b.recv()))

a, b = PC(), PC()
a.nic.drop(1)
b.nic.drop(1,2,3)
l = link(a, b)
run()
