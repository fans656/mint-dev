class Signal(object):

    def __init__(self, *types):
        self.fs = []

    def connect(self, f):
        self.fs.append(f)

    def emit(self, *args, **kwargs):
        for f in self.fs:
            f(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        self.emit(*args, **kwargs)
