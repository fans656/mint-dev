from protocol import Protocol

def n_ones(bits):
    return sum(1 for b in bits if b == '1')

def is_odd(n):
    return bool(n & 1)

def is_even(n):
    return not is_odd(n)

def even_parity_bit(bits):
    return '1' if is_odd(n_ones(bits)) else '0'

def odd_parity_bit(bits):
    return '1' if is_even(n_ones(bits)) else '0'

def make_even_parity(bits):
    return bits + even_parity_bit(bits)

def make_odd_parity(bits):
    return bits + odd_parity_bit(bits)

def is_even_parity(bits):
    return is_even(n_ones(bits))

def is_odd_parity(bits):
    return is_odd(n_ones(bits))

class EvenParityProtocol(Protocol):

    def before_send(self):
        self.bits = make_even_parity(self.bits)

    def after_recv(self):
        if not is_even_parity(self.bits):
            raise Protocol.ErrorDetected('parity should be even')
        self.bits = self.bits[:-1]

class OddParityProtocol(Protocol):

    def before_send(self):
        self.bits = make_odd_parity(self.bits)

    def after_recv(self):
        if not is_odd_parity(self.bits):
            raise Protocol.ErrorDetected('parity should be odd')
        self.bits = self.bits[:-1]

if __name__ == '__main__':
    bits = '11000'
    print make_even_parity(bits)
    print make_odd_parity(bits)
