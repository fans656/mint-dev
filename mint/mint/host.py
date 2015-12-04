from collections import OrderedDict, defaultdict, deque

import mint
from mint import protocols
from mint.core import Entity
from mint.nic import NIC
from mint.exceptions import Empty, Full
from mint.cachetable import CacheTable
from mint.libsocket import LibSocket
from mint.pdus import (
    Data, Frame, Packet, Datagram, ARP,
    IP, Port, MAC,
    ip_from_user, mac_from_user, port_from_user,
    IP_Loopback,
    MAC_Invalid, MAC_Broadcast,
    Discomposer,
)

class Host(Entity):

    def __init__(self, **kwargs):
        super(Host, self).__init__(n_tips=1)
        self.tip = self.tips[0]
        self.nic = NIC(self.tip)
        self.libsocket = LibSocket(self)

        self.ip = kwargs.get('ip', '1.0.0.{}'.format(self.index))
        self.mac = kwargs.get('mac', self.index)

        self.arp = protocols.ARP(self)
        self.arp.updated.connect(self._send_pending_packets)
        self.ip2mac = self.arp.ip2mac
        self.arp_table = self.ip2mac

        self.pending_packets = defaultdict(deque)
        self.pending_raws = deque()

    @property
    def ip(self):
        return self._ip

    @ip.setter
    def ip(self, val):
        self._ip = ip_from_user(val)

    @property
    def mac(self):
        return self._mac

    @mac.setter
    def mac(self, val):
        self._mac = mac_from_user(val)

    def send(self, data, ip=None, port=None, mac=None,
             protocol=None,
             ethertype=None):

        def given(*args):
            all_args = set((ip, port, mac, protocol, ethertype))
            cur_args = set(args)
            return all(args) and not any(all_args - cur_args)

        if isinstance(data, str):
            cvt = lambda f, v: f(v) if v else v
            ip = cvt(IP, ip)
            port = cvt(Port, port)
            mac = cvt(MAC, mac)
            # raw data in preamble/postabmle
            if given():
                self.send_raw(data)
            # raw data in Ethernet frame
            elif given(mac):
                frame = Frame(
                    dst_mac=mac,
                    src_mac=self.mac,
                    ethertype=Frame.EtherType.Raw,
                    payload=data,
                )
                self.send_frame(frame)
            # raw data in IPv4 packet
            elif given(ip):
                packet = Packet(
                    src_ip=self.ip,
                    dst_ip=ip,
                    protocol=Packet.Protocol.Raw,
                    payload=data,
                )
                self.send_packet(packet, ethertype=Frame.EtherType.IPv4)
            else:
                raise NotImplementedError("don't know how to send")

    def send_raw(self, data):
        self.pending_raws.append(data)

    def send_frame(self, frame):
        self.send_raw(frame.raw)

    def send_packet(self, packet, ethertype):
        if packet.dst_ip == IP_Loopback:
            self.report('loopback packet, ignored')
            return
        try:
            dst_ip = packet.dst_ip
            dst_mac = self.ip2mac[dst_ip]
        except KeyError:
            self.pending_packets[dst_ip].append((packet, ethertype))
            self.arp.query(dst_ip)
        else:
            frame = Frame(
                dst_mac=dst_mac,
                src_mac=self.mac,
                ethertype=ethertype,
                payload=packet.raw,
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
                payload=p.raw,
            )
            self.send_frame(f)

    def run(self):
        while True:
            self.do_send()
            self.do_recv()
            mint.elapse(1)

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
            self.on_frame(raw)

    def on_frame(self, raw):
        frame = Frame(raw)
        if frame.ethertype == Frame.EtherType.ARP:
            self.arp.process(frame.payload)
        elif frame.ethertype == Frame.EtherType.IPv4:
            self.on_ipv4(frame)
        elif frame.ethertype in (Frame.EtherType.Raw,):
            self.report(
                'unsupported frame type "{}", ignored',
                Frame.EtherType[frame.ethertype],
            )
        else:
            self.report('unknown frame type, ignored')

    def on_ipv4(self, frame):
        packet = Packet(frame.payload)
        src_ip = packet.src_ip
        src_mac = frame.src_mac
        self.ip2mac[src_ip] = src_mac
        if packet.protocol == Packet.Protocol.UDP:
            datagram = Datagram(packet.payload)
            try:
                sock_id = (self.libsocket.SOCK_DGRAM,
                           packet.dst_ip, datagram.dst_port)
                sock = self.sockets[sock_id]
                remote_addr = (packet.src_ip, datagram.src_port)
                sock.feed_datagram(datagram.payload, remote_addr)
            except KeyError:
                pass
        else:
            self.report(
                'got IPv4 packet of unsupport protocol {}, ignored',
                Packet.Protocol[packet.protocol],
            )

    def sending(self, at):
        return self.nic.sending

    def sent(self, at):
        return self.nic.sent

    @property
    def status(self):
        nic = OrderedDict([
            ('nic', self.nic),
            ('tip', self.tip),
        ])
        return [
            ('IP:{} MAC:{}'.format(self.ip, self.mac), nic),
            ('O', Discomposer(lambda: self.nic.odata)),
            ('I', Discomposer(lambda: self.nic.idata)),
        ]
