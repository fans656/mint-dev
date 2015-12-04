class Protocol(object):

    DelegatedAttributes = set([
        'report', 'ip', 'mac',
        'send_raw',
        'send_frame',
    ])

    def __init__(self, host):
        self.host = host

    def __getattribute__(self, name):
        sup = super(Protocol, self)
        if name in type(self).DelegatedAttributes:
            host = sup.__getattribute__('host')
            return getattr(host, name)
        return sup.__getattribute__(name)

    def __setattr__(self, name, val):
        sup = super(Protocol, self)
        if name in type(self).DelegatedAttributes:
            host = sup.__getattribute__('host')
            setattr(host, name, val)
        sup.__setattr__(name, val)

    def __delattr__(self, name):
        sup = super(Protocol, self)
        if name in type(self).DelegatedAttributes:
            host = sup.__getattribute__('host')
            delattr(host, name)
        sup.__delattr__(name)

class Signal(object):

    def __init__(self, *types):
        self.fs = []

    def connect(self, f):
        self.fs.append(f)

    def emit(self, *args, **kwargs):
        for f in self.fs:
            f(*args, **kwargs)
