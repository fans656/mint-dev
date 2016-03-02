import mint
from mint.interface import Interface
from mint.routetable import RouteTable
from mint.core import EntityWithNIC
from mint.utils import each
from mint.pdus import (
    Packet,
)

class Router(EntityWithNIC):

    def __init__(self, n_interfaces=3):
        super(Router, self).__init__(n_interfaces)
        self.interfaces = [Interface(self, nic) for nic in self.nics]
        each(self.interfaces).report.connect(self.report)
        each(self.interfaces).on_ipv4.connect(self.on_ipv4)
        self.routes = RouteTable()

    def on_ipv4(self, frame, **kwargs):
        i_interface = kwargs.get('interface')
        packet = Packet(frame.payload)
        try:
            net, _, gateway, interface = self.routes.find(packet.dst_ip)
        except KeyError:
            self.report('do not know how to route packet for {}',
                        packet.dst_ip)
        else:
            if interface != i_interface:
                interface.send_packet(
                    data=packet.raw,
                    dst_ip=gateway if gateway else packet.dst_ip,
                    ethertype=frame.ethertype,
                )
            else:
                self.report('packet dst to {} already on net {}, ignored',
                            packet.dst_ip, net)

    def __getitem__(self, index):
        return self.interfaces[index]

    def run(self):
        while True:
            each(self.interfaces).do_send()
            each(self.interfaces).do_recv()
            mint.elapse(1)

    @property
    def status(self):
        return [
            ('routes', lambda: self.routes),
        ] + [
            ('if{}'.format(i), interface)
            for i, interface in enumerate(self.interfaces)
        ]
