def bitify(data):
    return ''.join(bin(ord(byte))[2:] for byte in data)

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
    a = [1,2,3,4,5]
    print split(a, lambda t: t % 2 == 0)
