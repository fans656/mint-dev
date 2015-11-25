import sys
from f6 import each, bunch

def put(*args):
    s = ' '.join(map(str, args))
    sys.stdout.write(s + '\n')

def new_name(obj, reset=True):
    cls = type(obj)
    if not hasattr(cls, 'n_instances'):
        cls.n_instances = 0
    n = cls.n_instances
    cls.n_instances += 1
    return '{} {}'.format(cls.__name__, n)
