import sys

def put(*args):
    sys.stdout.write(put_format(*args) + '\n')

def put_format(*args):
    fmt = args[0]
    if isinstance(fmt, str) and '{' in fmt:
        s = fmt.format(*args[1:])
    else:
        s = ' '.join(map(str, args))
    return s

def new_name(obj, reset=True):
    cls = type(obj)
    if not hasattr(cls, 'n_instances'):
        cls.n_instances = 0
    n = cls.n_instances
    cls.n_instances += 1
    return '{} {}'.format(cls.__name__, n)

class bunch(dict):

    def __init__(self, **kwargs):
        super(bunch, self).__init__(kwargs)
        self.__dict__.update(kwargs)
