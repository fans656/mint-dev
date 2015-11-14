'''
stop-and-wait protocol

a will wait for an acknowledgement after every frame it sent
upon which the next frame is then sent
b will give a acknowledgement everytime it `recv` a frame

the acknowledgement consists of no data at all
(just preamble+postamble so receiver can recognize it)

you can comment out the `a.nic.recv()` call
so a won't wait for the acknowledgement
then you will notice considerable frame losses
uncomment it will give the result where no frame is lost
but as you can see, the processing speed is receivably slower
'''
import mint
from mint import *

@actor
def _():
    for _ in xrange(64):
        a.nic.send('\x01')
        a.nic.recv() # try comment this out

@actor
def _():
    while True:
        b.nic.recv()
        wait(48)
        b.nic.send('')

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
