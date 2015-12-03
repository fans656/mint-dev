import sys
import itertools

from mint.utils import each, bunch

def put(*args):
    s = ' '.join(map(str, args))
    sys.stdout.write(s + '\n')

def takewhile(pred, dq):
    ret = list(itertools.takewhile(lambda e: pred(e), dq))
    [dq.popleft() for _ in xrange(len(ret))]
    return ret
