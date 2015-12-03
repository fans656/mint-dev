'''
monitor NIC's frame receiving behavior
output the # of dropped, handed, detected frames
change
    data sent by `a`
    b.nic.buffer_size
    # of frames sent by `a`
to see different behaviors
'''
import mint
from mint import *

@actor
def _():
    for _ in xrange(64):
        a.nic.send('\x01')

@actor
def _():
    while True:
        b.nic.recv()
        wait(24)

@after_worker_input
def _():
    nic = b.nic
    if nic.frame_ended:
        put('dropped: {}, handed: {}, total detected: {}',
                nic.n_dropped_frames,
                nic.n_handed_frames,
                nic.n_detected_frames)

a, b = Host(), Host()
b.nic.buffer_size = 1
l = link(a, b)
run()
