__all__ = [
    'PDU',
    'Octet', 'Byte',
    'Word',
    'DWord',
    'Octets', 'Bytes',
]

class Octets(object):

    def __init__(self, n=0, variable=None):
        self.n = n
        self.variable = self.n == 0 if variable is None else variable

    def __call__(self, n=0):
        return Octets(self.n * n)

    def __str__(self):
        return '<Octets of length {}{}>'.format(
            len(self),
            '+' if self.variable else '')

    def __len__(self):
        return self.n

class Meta(type):

    def __init__(cls, name, bases, attrs):
        for k, v in attrs.items():
            if isinstance(v, Octets):

class PDU(Octets):

    __metaclass__ = Meta

    def __init__(self, raw=None):
        super(PDU, self).__init__()
        # used as a descriptor
        if raw is None:
            pass
        # used as a inspector
        else:
            pass

Octet = Octets(1)
Byte = Octet
Word = Octets(2)
DWord = Word(2)
Bytes = Octets

if __name__ == '__main__':
    print PDU
    print PDU()
    print Word()
