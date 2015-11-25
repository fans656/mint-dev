'''
tik tok

physical port will introduce a inherent 1 tik-tok delay
Link defaults to 0 delay

no initial sent setup
participate in the first tik-tok, send a bit
then do nothing in the next tik-tok
then send another bit
'''
from mint import *

a = Host()
b = Host()
l = Link(a, b)

@proc
def _():
    wait(0)
    a.port.send('1')
    wait()
    a.port.send('1')

@proc
def _():
    data = b.port.recv(10)
    print 'Received at {}: {}'.format(now(), data)
    stop()

run()
