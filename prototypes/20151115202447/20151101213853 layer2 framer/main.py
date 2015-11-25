'''
transport layer frame protocol
upper layer data is into payloads of 3 bytes
byte escaping payload
head & tail flag to determine frame's start end end

a sends 0x12 34 56 78
b receives 2 frames which are
    0x12 34 56
    0x78

send is operate on byte level
recv is operate on bit level due to preamble bits caused by latency
    (here the latency is 3, so preamble == '000')
and later development will take into account bit errors
'''
import mint
from mint.components import Link
from mint import utils
from mint.utils import format_bytes as fmt

from devices import PC

@mint.setup
def run(latency):
    @mint.proc()
    def sender():
        a.framer.send('\x12\x34\x56\x78')
        yield mint.end

    @mint.proc()
    def receiver():
        data = yield b.framer.recv()
        print 'bytes recv by {}: {}'.format(b, fmt(data, 'hex'))
        data = yield b.framer.recv()
        print 'bytes recv by {}: {}'.format(b, fmt(data, 'hex'))
        print 'bits ever received at {}: {}'.format(
                b.port,
                fmt(utils.unbitify(b.port.bits_received), 'bin'))
        print 'bits ever received at {} (shifted): {}'.format(
                b.port,
                fmt(utils.unbitify(b.port.bits_received[3:]), 'hex'))
        raise mint.Stop
        yield mint.end

    a = PC('a')
    b = PC('b')
    link = Link(a, b)
    link.latency = latency

run(latency=3)
#run(latency=2)
