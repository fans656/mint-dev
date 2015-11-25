from mint.components import Endpoint
from mint import utils
import mint

class PC(Endpoint):

    def __init__(self, name):
        super(PC, self).__init__(name)
        self.data = ''
        self.port.bit_arrive.connect(self.collect_bits)

    def collect_bits(self, port):
        # TODO
        # self.data += ibuffer.take_bytes()
        #
        # collect bits at multiples of 8
        bits, port.ibuffer = utils.split_at(port.ibuffer, len(port.ibuffer) // 8 * 8)
        if bits:
            self.data += utils.unbitify(bits)

    def send(self, data):
        self.port.put(data)

    @mint.block
    def recv(self, nbytes):
        while len(self.data) < nbytes:
            yield self.port.bit_arrive.event
        ret, self.data = utils.split_at(self.data, nbytes)
        mint.ret(ret)
