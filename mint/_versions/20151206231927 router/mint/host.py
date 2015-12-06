import mint
from mint.interface import Interface
from mint.routetable import RouteTable
from mint.core import EntityWithNIC
from mint.libsocket import LibSocket
from mint.pdus import (
    Frame, Packet,
    IP,
    Discomposer,
)

class Host(EntityWithNIC):

    def __init__(self, **kwargs):
        super(Host, self).__init__(n_interfaces=1)
        self.libsocket = LibSocket(self)

        ip = kwargs.get('ip', '192.168.0.1{:02}'.format(self.index))
        mask = kwargs.get('mask', '255.255.255.0')
        mac = kwargs.get('mac', None)

        self.interfaces = [Interface(self, nic, ip, mask, mac)
                           for nic in self.nics]
        self.interface = self.interfaces[0]
        self.interface.report.connect(self.report)
        self.interface.on_ipv4.connect(self.on_ipv4)

        self.routes = RouteTable(self)

    def send(self, data, ip, protocol=Packet.Protocol.Raw):
        dst_ip = IP(ip)
        _, _, gateway, interface = self.routes.find(dst_ip)

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

    @property
    def mask(self):
        return self.interface.mask

    @mask.setter
    def mask(self, val):
        self.interface.mask = val

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

    def on_ipv4(self, frame, **_):
        packet = Packet(frame.payload)
        self.send('wooo..', packet.src_ip)

    def run(self):
        while True:
            self.interface.do_send()
            self.interface.do_recv()
            mint.elapse(1)

    @property
    def status(self):
        nic_title = 'IP:{}/{} MAC:{}'.format(
            self.ip, self.mask.net_len, self.mac)
        return [
            (nic_title, self.nic),
            ('O', Discomposer(lambda: self.nic.odata)),
            ('I', Discomposer(lambda: self.nic.idata)),
        ]
