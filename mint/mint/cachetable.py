from collections import OrderedDict
import mint

class CacheTable(object):

    def __init__(self, entry_duration=float('inf')):
        self.entries = {}
        self.entry_duration = entry_duration

    def __getitem__(self, key):
        val, ctime = self.entries[key]
        if mint.now() - ctime > self.entry_duration:
            del self.entries[key]
            raise KeyError('entry expired')
        return val

    def __setitem__(self, key, val):
        self.entries[key] = (val, mint.now())

    @property
    def status(self):
        r = OrderedDict()
        for k, (v, time) in self.entries.items():
            r[k] = '{} ({})'.format(v, time)
        return r
