import functools
import random

def error_func(f):
    def f_(*args, **kwargs):
        @functools.wraps(f)
        def f__(bits):
            bits = f([b == '1' for b in bits], *args, **kwargs)
            return ''.join('1' if b else '0' for b in bits)
        return f__
    return f_

@error_func
def flip(bits, *iths):
    for i in iths:
        bits[i] = not bits[i]
    return bits

@error_func
def random_flip(bits, rate=0.01):
    if rate:
        n = int(1 / rate)
        for i, bit in enumerate(bits):
            if not random.randint(0, n-1):
                bits[i] = not bit
    return bits

@error_func
def id(bits):
    return bits

if __name__ == '__main__':
    #print dir(flip)
    #print dir(flip.func_code)
    #print flip.func_code.co_varnames
    print flip(5)('00000')
