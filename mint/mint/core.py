import struct, logging
from collections import deque, OrderedDict

import mint
from mint.utils import put_format

log = logging.getLogger('core')

class Tip(object):

    def __init__(self, host):
        self.host = host
        self.peer = None
        self.link = None
        self._osymbol = 0
        self.isymbol = 0

    @property
    def osymbol(self):
        return self._osymbol

    @osymbol.setter
    def osymbol(self, symbol):
        self._osymbol = symbol
        if self.peer:
            self.peer.isymbol = symbol

    def peer_with(self, tip, by=None):
        self.peer = tip
        self.peer.peer = self
        self.link = by
        self.peer.link = by

    @property
    def peer_host(self):
        return self.link.peer_of(self).host

    @property
    def status(self):
        return OrderedDict([
            ('isymbol', self.isymbol),
            ('osymbol', self.osymbol),
        ])

class Entity(object):

    class Meta(type):

        def __init__(cls, name, bases, attrs):
            if 'role' not in attrs:
                cls.role = name

    __metaclass__ = Meta

    def __init__(self, n_tips):
        self.tips = [Tip(self) for _ in xrange(n_tips)]
        self.stdout = []
        mint.add(self)
        self.statuses = []

    def __repr__(self):
        return '{} {}'.format(type(self).__name__, self.index)

    def report(self, *args, **kwargs):
        s = put_format(*args, **kwargs)
        self.stdout.append('{:5} | {}'.format(mint.now(), s))
        mint.report(self, '|', s)
