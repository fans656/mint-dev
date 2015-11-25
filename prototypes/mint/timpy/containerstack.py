import functools
from f6 import each

class ContainerStack(object):

    def __init__(self):
        self.layers = []

    # put(container, item)
    # get(container) -> item
    # broker(src_layer, dst_layer)
    def add_layer(self, container, get, put,
                  broker=lambda s,d: d.put(s.get())):
        self.layers.append(Layer(container, get, put, broker))

    def put(self, e):
        self.layers[0].put(e)

    def get(self, depth=0):
        top = self.layers[-1]
        #print top.container, bool(top.container)
        if not top:
            self.populate()
        if top:
            r = [top.get()]
            if depth:
                while any(self.layers[-depth:]):
                    r.extend(self.get())
        else:
            r = []
        return r


    def populate(self):
        for level in xrange(len(self.layers) - 1):
            lower, upper = self.layers[level:level+2]
            if lower and not upper:
                lower.broker(lower, upper)

    def __iter__(self):
        while self:
            yield self.get()

    def __nonzero__(self):
        return any(map(bool, self.layers))

    def __repr__(self):
        return '\n'.join(map(repr, each(self.layers).container))

class Layer(object):

    def __init__(self, container, get, put, broker):
        self.container = container
        self.get = functools.partial(get, container)
        self.put = functools.partial(put, container)
        self.broker = broker

    def __nonzero__(self):
        return bool(self.container)
