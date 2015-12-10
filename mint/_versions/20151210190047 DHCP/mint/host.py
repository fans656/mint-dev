import mint
from mint import Signal
from mint.interface import Interface
from mint.routetable import RouteTable
from mint.core import EntityWithNIC
from mint.libsocket import LibSocket
from mint.protocols.dhcp import DHCPClient
from mint.pdus import (
    Frame, Packet, Datagram,
    IP, Port,
    IP_Broadcast,
    Discomposer,
)

class Host(EntityWithNIC):

    def __init__(self, **kwargs):
        super(Host, self).__init__(n_interfaces=1)
        self.libsocket = LibSocket(self)
        self.sockets = {
            Packet.Protocol.TCP: {},
            Packet.Protocol.UDP: {},
        }

        ip = kwargs.get('ip', None)
        mac = kwargs.get('mac', None)

        self.interfaces = [Interface(self, nic, ip, mac) for nic in self.nics]
        self.interface = self.interfaces[0]
        self.interface.on_ipv4.connect(self.on_ipv4)
        self.interface.report.connect(self.report)

        self.routes = RouteTable(self)

        self.dhcp_client = DHCPClient(self)

    def send_udp(self, data, src_port, dst_ip, dst_port):
        src_port = Port(src_port)
        dst_port = Port(dst_port)
        datagram = Datagram(
            src_port=src_port,
            dst_port=dst_port,
            payload=data,
        )
        self.send_ip(datagram.raw, dst_ip, protocol=Packet.Protocol.UDP)

    def send_ip(self, data, dst_ip, protocol=Packet.Protocol.Raw):
        dst_ip = IP(dst_ip)
        if not dst_ip:
            self.report('invalid dst_ip {}, ignored', dst_ip)
            return
        try:
            _, _, gateway, interface = self.routes.find(dst_ip)
        except KeyError:
            self.report('no gateway for destination {}, ignored', dst_ip)
            return

        if gateway:
            self.report('{} is non-local, beg {} to deliver', dst_ip, gateway)
        else:
            self.report('{} is local, send directly', dst_ip)

        packet = Packet(
            src_ip=interface.ip,
            dst_ip=dst_ip,
            protocol=protocol,
            payload=data,
        )
        interface.send_packet(
            packet.raw,
            gateway if gateway else dst_ip,
            Frame.EtherType.IPv4,
        )

    @property
    def ip(self):
        return self.interface.ip

    @ip.setter
    def ip(self, val):
        self.interface.ip = val
        self.report('ip changed to {}', self.interface.ip)

    @property
    def mask(self):
        return self.interface.mask

    @mask.setter
    def mask(self, val):
        self.interface.mask = val
        self.report('subnet mask changed to {}', self.interface.mask)

    @property
    def mac(self):
        return self.interface.mac

    @mac.setter
    def mac(self, val):
        self.interface.mac = val

    @property
    def default_gateway(self):
        return self._default_gateway

    @default_gateway.setter
    def default_gateway(self, val):
        gateway = IP(val)
        self._default_gateway = gateway
        self.routes[-1].gateway = gateway
        self.report('default gateway changed to {}', gateway)

    def on_ipv4(self, frame, **_):
        packet = Packet(frame.payload)
        if packet.protocol == Packet.Protocol.UDP:
            self.on_udp(packet)

    def on_udp(self, packet):
        datagram = Datagram(packet.payload)
        try:
            addr2socket = self.sockets[packet.protocol]
        except KeyError:
            self.report(
                'UDP({}:{} -> {}:{}): {}',
                packet.src_ip, datagram.src_port,
                packet.dst_ip, datagram.dst_port,
                repr(datagram.payload),
            )
        else:
            ip, port = packet.dst_ip, datagram.dst_port
            if ip == IP_Broadcast:
                ip = self.ip
            try:
                sock = addr2socket[(ip, port)]
            except KeyError:
                self.report(
                    'no handler at {} {}:{}, ignored',
                    Packet.Protocol[packet.protocol],
                    packet.dst_ip, datagram.dst_port,
                )
            else:
                sock.feed_datagrams(datagram, packet.src_ip)

    def run(self):
        if not self.ip:
            self.dhcp = DHCPClient(self)
        while True:
            self.interface.do_send()
            self.interface.do_recv()
            mint.elapse(1)

    def bind(self, sock, addr):
        ip, port = addr

        ip = IP(ip)
        if not ip:
            ip = self.interface.ip

        port = Port(port) # TODO: port == None

        addr = (ip, port)

        if sock.type == LibSocket.SOCK_DGRAM:
            addr2socket = self.sockets[Packet.Protocol.UDP]
        else:
            self.report('invalid bind')
            return (None, None)
        addr2socket[addr] = sock
        return addr

    @property
    def status(self):
        nic_title = 'IP:{}/{} MAC:{}'.format(
            self.ip, self.mask.net_len, self.mac)
        return [
            (nic_title, self.interface),
            ('O', Discomposer(lambda: self.nic.odata)),
            ('I', Discomposer(lambda: self.nic.idata)),
        ]
