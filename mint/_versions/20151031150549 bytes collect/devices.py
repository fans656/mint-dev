from mint.components import Endpoint
from mint import utils

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
            print '{} Collected: {}'.format(self, utils.format_bytes(self.data))
            raw_input()
