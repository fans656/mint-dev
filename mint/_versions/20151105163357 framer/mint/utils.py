def bitify(data):
    return ''.join('{:08b}'.format(ord(byte)) for byte in data)

def unbitify(bits):
    return ''.join(chr(int(bits[i:i+8], 2)) for i in range(0, len(bits), 8))

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

def view_queue(q):
    import Queue
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
    import random
    return ''.join('1' if random.randint(0,1) else '0'
            for _ in range(length))

def put(s, *args, **kwargs):
    import sys
    if isinstance(s, str) or isinstance(s, unicode):
        if args and kwargs:
            s = s.format(*args, **kwargs)
    else:
        s = ' '.join(map(str, (s,) + args))
    sys.stdout.write(s + '\n')

class Bunch(object):

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

if __name__ == '__main__':
    for _ in range(8):
        print randombits()
