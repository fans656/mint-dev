import mint
from mint import utils

class BitStuffingFramer(object):

    def __init__(self, port=None):
        self.port = port
        self.flag = '01111110'

    def send(self, bits):
        bits = self.bit_stuff(bits)
        self.port.send(bits)

    def recv(self):
        self.detect_preamble()
        return self.get_payload()

    def bit_stuff(self, bits, postamble=True):
        ret = self.flag
        count = 0
        for bit in bits:
            ret += bit
            if bit == '1':
                count += 1
                if count == 5:
                    ret += '0'
                    count = 0
            else:
                count = 0
        if postamble:
            ret += self.flag
        return ret

    def detect_preamble(self):
        '''
        Detect preamble and return the bits received before the preamble unstuffed.

        Actually, it will recognize 6 consecutive '1' bit as a preamble.
        Some example:
            Received            Returned
            001111110           '0'
            101111110           '1'
            111111              ''         # note this!
            01010111111         '01010'
            111110111111        '111110'
        '''
        bits = ''
        count = 0
        for bit in self.port.recv():
            if bit == '1':
                bits += bit
                count += 1
                if count == 6:
                    bits += self.port.recv(1)
                    break
            else:
                if count != 5:
                    bits += bit
                count = 0
        return bits[:-8]

    get_payload = detect_preamble

if __name__ == '__main__':
    import functools

    class Port(object):

        def __init__(self, bits=''):
            self.bits = bits

        def send(self, bits):
            self.bits = bits

        def recv(self, nbits=0):
            if not nbits:
                return iter(functools.partial(self.recv, 1), '')
            bits, self.bits = utils.split_at(self.bits, nbits)
            return bits

    for _ in range(8):
        data = utils.random_bits(800)
        framer = BitStuffingFramer(Port())
        framer.send(data)
        assert data == framer.recv()
    print 'No error right? Excited!'
