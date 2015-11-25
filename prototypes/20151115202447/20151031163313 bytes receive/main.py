'''
    sender sends 2 bytes separated by 4 seconds
    receiver receives 4 bytes at 32th seconds

    you can variate the time elapsed after the first byte sent
    and the link's latency (strictly correspond to the preamble bits received)
'''
import mint
from mint.components import Link
from mint.utils import format_bytes as fmt

from devices import PC

@mint.setup
def run(sep, latency):
    @mint.proc()
    def sender():
        a.port.put('\xff')
        yield mint.env.timeout(sep)
        a.port.put('\xff')
        yield mint.end

    @mint.proc()
    def receiver():
        data = yield b.recv(4)
        print 'Received at {}: {}'.format(mint.env.now, fmt(data, 'hex'))
        print '                {}'.format(fmt(data, 'bin'))
        raise mint.Stop
        yield mint.end

    a = PC('a')
    b = PC('b')
    link = Link(a, b)
    link.latency = latency

run(sep=4, latency=8)
run(sep=9, latency=2)
