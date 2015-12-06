from namedlist import namedlist
from mint.pdus import IP

class RouteTable(object):

    def __init__(self, host=None):
        self.entries = []
        if host:
            # local subnet
            self.add(
                host.ip & host.mask,
                host.mask,
                '0.0.0.0',
                host.interface)
            # default gateway
            self.add(
                '0.0.0.0',
                '0.0.0.0',
                '0.0.0.0',
                host.interface)

    def find(self, dst_ip):
        try:
            return next(e for e in self.entries if dst_ip & e.mask == e.net)
        except StopIteration:
            raise KeyError('no matching entry for {}'.format(dst_ip))

    def add(self, net, mask, gateway, interface):
        self.entries.append(Entry(
            IP(net),
            IP(mask),
            IP(gateway),
            interface))

    def __getitem__(self, index):
        return self.entries[index]

    def __iter__(self):
        return iter(self.entries)

    def __repr__(self):
        s = '{:16} {:16} {:16} {:16}\n'.format(
            'Network', 'Mask', 'Gateway', 'Interface')
        for net, mask, gateway, interface in self:
            s += '{:16} {:16} {:16} {:16}\n'.format(
                net, mask, gateway, interface.ip)
        return s

Entry = namedlist('Entry', ['net', 'mask', 'gateway', 'interface'])
