import sys
import random
import Queue
from collections import deque

def bitify(bytes):
    return ''.join('{:08b}'.format(ord(byte)) for byte in bytes)

def unbitify(bits):
    return ''.join(chr(int(bits[i:i+8], 2)) for i in range(0, len(bits), 8))

def to_bits(byte):
    mask = 0x80
    bits = [0] * 8
    for i in xrange(8):
        bits[i] = 1 if byte & mask else 0
        mask >>= 1
    return bits

def to_byte(bits):
    byte = 0
    mask = 0x80
    for bit in bits:
        if bit:
            byte |= mask
        mask >>= 1
    return byte

def listify_bits(bits):
    return (1 if b == '1' else 0 for b in bits)

def unlistify_bits(bits):
    return ''.join('1' if b else '0' for b in bits)

def bitwise_or(*datas):
    nbits = len(datas[0])
    return ''.join('1' if any(data[i] == '1' for data in datas) else '0'
            for i in range(nbits))

def format(bytes, type='hex'):
    if type == 'hex':
        return ' '.join('{:02x}'.format(ord(byte)) for byte in bytes)
    elif type == 'bin':
        return ' '.join('{:08b}'.format(ord(byte)) for byte in bytes)

def split(xs, *preds):
    if not preds:
        return xs
    if len(preds) == 1:
        preds += (lambda t: not preds[0](t),)
    rss = [[] for _ in preds]
    for x in xs:
        for rs, yes in zip(rss, map(lambda p: p(x), preds)):
            if yes:
                rs.append(x)
    return rss

def split_into(xs, group_size):
    return [xs[i:i+group_size] for i in range(0, len(xs), group_size)]

def split_at(xs, index):
    return xs[:index], xs[index:]

def group(xs, size):
    xs = list(xs)
    for i in xrange(0, len(xs), size):
        yield xs[i:i+size]

def view_queue(q):
    a = []
    while True:
        try:
            a.append(q.get(block=False))
        except Queue.Empty:
            break
    for t in a:
        q.put(t)
    return a

def random_bits(length=8):
    return ''.join('1' if random.randint(0,1) else '0'
            for _ in range(length))

def put(s, *args, **kwargs):
    def fmt(t):
        if isinstance(t, Queue.Queue):
            t = view_queue(t)
        return str(t)
    if (isinstance(s, str) or isinstance(s, unicode)) and '{' in s:
        if args or kwargs:
            s = s.format(*args, **kwargs)
    else:
        s = ' '.join(map(fmt, (s,) + args))
    sys.stdout.write(s + '\n')

class Bunch(object):

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

class PatternDetector(object):

    def __init__(self, pattern):
        self.pattern = tuple(pattern)
        self.data = deque(maxlen=len(pattern))

    def feed(self, item):
        self.data.append(item)
        ret = tuple(self.data) == self.pattern
        if ret:
            self.clear()
        return ret

    def clear(self):
        self.data.clear()

if __name__ == '__main__':
    print to_bits('\xff')
