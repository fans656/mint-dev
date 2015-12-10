import itertools
from collections import OrderedDict, defaultdict, deque
from bitarray import bitarray

import mint
from mint import protocols, Signal
from mint.core import EntityWithNIC
from mint.exceptions import Empty, Full
from mint.cachetable import CacheTable
from mint.libsocket import LibSocket
from mint.pdus import (
    BadFormat,
    Data, Frame, Packet, Datagram, ARP,
    IP, Port, MAC,
    ip_from_user, mac_from_user, port_from_user,
    IP_Loopback,
    MAC_Invalid, MAC_Broadcast,
    Discomposer,
)

class Interface(object):

    mac_address = itertools.count(1)

    def __init__(self, host, nic, ip=None, mac=None):
        self.host = host
        self.nic = nic
        self.ip = ip if ip is not None else '0.0.0.0/0'
        self.mac = mac if mac is not None else next(Interface.mac_address)

        self.report = Signal()
        self.on_ipv4 = Signal()

        self.arp = protocols.ARP(self)
        self.ip2mac = self.arp.ip2mac
        self.arp_table = self.ip2mac
        self.arp.updated.connect(self._send_pending_packets)
        self.arp.send_frame.connect(self.send_frame)
        self.arp.report.connect(self.report)

        self.pending_packets = defaultdict(deque)
        self.pending_raws = deque()

    @property
    def ip(self):
        return self._ip

    @ip.setter
    def ip(self, val):
        if isinstance(val, str):
            if '/' not in val:
                raise ValueError(
                    'interface need subnet mask (e.g. "{}/24")'.format(val))
            val, net_len = val.split('/')
            net_len = int(net_len)
            mask = '1' * net_len + '0' * (32 - net_len)
            self.mask = IP.from_bits(bitarray(mask))
        self._ip = ip_from_user(val)

    @property
    def mask(self):
        return self._mask

    @mask.setter
    def mask(self, val):
        self._mask = ip_from_user(val)

    @property
    def mac(self):
        return self._mac

    @mac.setter
    def mac(self, val):
        self._mac = mac_from_user(val)

    def send_raw(self, data):
        self.pending_raws.append(data)

    def send_frame(self, frame):
        self.send_raw(frame.raw)

    def send_packet(self, data, dst_ip, ethertype):
        if not dst_ip:
            self.report('invalid dst_ip {}, ignored', dst_ip)
            return
        try:
            dst_mac = self.ip2mac[dst_ip]
        except KeyError:
            self.pending_packets[dst_ip].append((data, ethertype))
            self.arp.query(dst_ip)
        else:
            frame = Frame(
                dst_mac=dst_mac,
                src_mac=self.mac,
                ethertype=ethertype,
                payload=data,
            )
            self.send_frame(frame)

    def _send_pending_packets(self, ip, mac):
        ps = self.pending_packets[ip]
        if not ps:
            return
        self.report('send pending {} packet(s) for {}', len(ps), ip)
        while ps:
            p, ethertype = ps.popleft()
            f = Frame(
                ethertype=ethertype,
                dst_mac=mac,
                src_mac=self.mac,
                payload=p,
            )
            self.send_frame(f)

    def do_send(self):
        try:
            raw = self.pending_raws[0]
            self.nic.send(raw, block=False)
            self.pending_raws.popleft()
        except IndexError:
            pass
        except Full:
            pass

    def do_recv(self):
        try:
            raw = self.nic.recv(block=False)
        except Empty:
            pass
        else:
            try:
                self.on_frame(raw)
            except BadFormat:
                self.report('bad data, ignored')

    def on_frame(self, raw):
        frame = Frame(raw)
        if frame.ethertype == Frame.EtherType.ARP:
            self.arp.process(frame.payload)
        elif frame.ethertype == Frame.EtherType.IPv4:
            self.on_ipv4(frame, interface=self)
        elif frame.ethertype in (Frame.EtherType.Raw,):
            self.report(
                'unsupported frame type "{}", ignored',
                Frame.EtherType[frame.ethertype],
            )
        else:
            self.report('unknown frame type, ignored')

    @property
    def status(self):
        return OrderedDict([
            ('IP', self.ip),
            ('Mask', self.mask),
            ('MAC', self.mac),
            ('ARP', self.arp_table),
            ('NIC', self.nic),
            ('O', Discomposer(lambda: self.nic.odata)),
            ('I', Discomposer(lambda: self.nic.idata)),
        ])
