def bitify(data):
    return ''.join('{:08b}'.format(ord(byte)) for byte in data)

def unbitify(bits):
    return ''.join(chr(int(bits[i:i+8], 2)) for i in range(0, len(bits), 8))

def format_bytes(bytes):
    return ' '.join('{:02x}'.format(ord(byte)) for byte in bytes)

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

def split_at(xs, index):
    return xs[:index], xs[index:]

if __name__ == '__main__':
    t = bitify('hi\x03')
    print t
    t = unbitify(t)
    print repr(t)
