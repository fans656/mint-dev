from collections import deque, OrderedDict
import struct
import logging
import mint
from mint import simulation, utils
from mint.exceptions import Full, Empty
from mint.protocols.delimiter import BitDelimiter
from mint.protocols.framer import Framer
from mint.protocols.packeter import Packeter
from mint.protocols.pdus import Frame, Packet, MAC, Discomposer
from mint.utils import (
    each, bunch,
    ip_to_str, ip_from_str,
    mac_from_bytes, mac_to_bytes
)

log = logging.getLogger('component')

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
        mint.add(self)

    def __repr__(self):
        return '{} {}'.format(type(self).__name__, self.index)

    @property
    def status(self):
        return {'{}'.format(self): 'nothing'}

class Host(Entity):

    def __init__(self, ip=None, mac=None):
        super(Host, self).__init__(n_tips=1)
        self.tip = self.tips[0]

        if mac is None:
            mac = self.index + 1
        if ip is None:
            ip = '1.0.0.{}'.format(self.index + 1)

        # physical layer - frame delimiter
        self.delimiter = BitDelimiter(self.tip)
        # link layer - flow control
        self.framer = Framer(self.delimiter, mac_to_bytes(mac))
        # network layer - ARP
        self.packeter = Packeter(self.framer, ip_from_str(ip))

    @property
    def status(self):
        nic = OrderedDict([
            ('ip', '{}'.format(self.ip)),
            ('mac', '{:02x}'.format(self.mac)),
            ('nic', self.delimiter),
            ('tip', self.tip),
        ])
        return [('nic', nic),
                ('opdu', Discomposer(lambda: self.delimiter.odata)),
                ('ipdu', Discomposer(lambda: self.delimiter.idata)),
                ]

    @property
    def mac(self):
        return mac_from_bytes(self.framer.mac)

    @mac.setter
    def mac(self, val):
        self.framer.mac = mac_to_bytes(val)

    @property
    def ip(self):
        return ip_to_str(self.packeter.ip)

    @ip.setter
    def ip(self, val):
        self.packeter.ip = ip_from_str(val)

    def l3send(self, data, to, protocol=Packet.Protocol.Raw):
        self.packeter.send(data, to=ip_from_str(to), protocol=protocol)

    def l2send(self, data, to):
        self.framer.send(data, mac_to_bytes(to))

    def l2recv(self):
        return self.framer.recv()

    def sending(self, at):
        return self.delimiter.sending

    def sent(self, at):
        return self.delimiter.sent

class Hub(Entity):

    def __init__(self, n_tips=3):
        super(Hub, self).__init__(n_tips)

class Switch(Entity):

    def __init__(self, n_tips=3):
        super(Switch, self).__init__(n_tips)
        self.ports = [BitDelimiter(tip) for tip in self.tips]
        self.routes = Switch.Routes(self.ports)
        mint.worker(self.run, priority=simulation.SWITCH_PRIORITY)

    def run(self):
        while True:
            self.routes.remove_expired_entries()
            for iport in self.ports:
                try:
                    raw = iport.recv(block=False)
                except Empty:
                    continue
                frame = Frame(raw)
                self.routes.register(frame.src, iport)
                oports = self.routes.get(frame.dst, exclude=iport)
                for oport in oports:
                    try:
                        oport.send(raw, block=False)
                    except Full:
                        mint.report('frame dropped {}', repr(raw))
            mint.elapse(1)

    @property
    def status(self):
        r = [('route table', self.routes)]
        r += [
            ('port-{}'.format(i), port)
            for i, port in enumerate(self.ports)
        ]
        return r

    def sending(self, at):
        return at.master.sending

    def sent(self, at):
        return at.master.sent

    class Routes(object):

        def __init__(self, ports, entry_duration=500):
            self.ports = ports
            self.entry_duration = entry_duration
            self.route_table = {
                MAC.Broadcast: bunch(ports=self.ports, time=float('inf'))
            }

        def remove_expired_entries(self):
            now = mint.now()
            n_entries = len(self.route_table)
            self.route_table = {
                k: v for k, v in self.route_table.items()
                if now - v.time < self.entry_duration
            }
            if len(self.route_table) != n_entries:
                mint.report('switch\'s expired entries cleaned')

        def register(self, addr, port):
            mint.report('register host with address {:02x} on port-{}',
                        mac_from_bytes(addr), self.ports.index(port))
            if addr == '\x00':
                return
            self.route_table[addr] = bunch(ports=[port], time=mint.now())

        def get(self, addr, exclude=None):
            try:
                ports = self.route_table[addr].ports
            except KeyError:
                ports = self.ports
            return [p for p in ports if p != exclude]

        @property
        def status(self):
            r = OrderedDict()
            for addr, entry in self.route_table.items():
                addr = '{:02x}'.format(mac_from_bytes(addr))
                ports = map(lambda p: self.ports.index(p), entry.ports)
                time = entry.time
                r[addr] = '{} {}'.format(ports, time)
            return r

class Router(Entity):

    def __init__(self, n_tips=3):
        super(Router, self).__init__(n_tips=n_tips)

class Link(Entity):

    def __init__(self, a, b, latency=0):
        super(Link, self).__init__(n_tips=2)
        a.peer_with(self.tips[0], by=self)
        self.tips[1].peer_with(b, by=self)
        self.latency = latency
        self.pipes = [deque([0] * self.latency) for _ in xrange(2)]
        self.endpoint_names = map(str, each(self.tips).peer.host)
        mint.worker(self.run, priority=simulation.LINK_PRIORITY)

    def peer_of(self, tip):
        return next(t for t in self.tips if t != tip.peer).peer

    def run(self):
        while True:
            self.transfer(self.tips[0], self.pipes[0], self.tips[1])
            self.transfer(self.tips[1], self.pipes[1], self.tips[0])
            mint.elapse(1)

    def transfer(self, itip, pipe, otip):
        pipe.appendleft(itip.isymbol)
        otip.osymbol = pipe.pop()

    @property
    def status(self):
        name0, name1 = self.endpoint_names
        pipe_name0 = '{} -> {}'.format(name0, name1)
        pipe_name1 = '{} -> {}'.format(name1, name0)
        return OrderedDict((
            (pipe_name0, ''.join(map(str, self.pipes[0]))),
            (pipe_name1, ''.join(map(str, self.pipes[1]))),
        ))

    def __getitem__(self, entity):
        return next(tip.peer for tip in self.tips if tip.peer.host == entity)

def link(a, b, *args, **kwargs):
    def to_tip(o):
        if isinstance(o, Host):
            return o.tip
        elif isinstance(o, Tip):
            return o
    return Link(to_tip(a), to_tip(b), *args, **kwargs)
