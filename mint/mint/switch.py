from collections import OrderedDict
import mint
from mint import simulation
from mint.core import Entity
from mint.nic import NIC
from mint.exceptions import Empty, Full
from mint.cachetable import CacheTable
from mint.utils import each
from mint.pdus import (
    Frame, MAC,
    MAC_Loopback,
    UnknownFormat,
)

class Switch(Entity):

    def __init__(self, n_tips=3):
        super(Switch, self).__init__(n_tips)
        self.nics = [NIC(tip) for tip in self.tips]
        self.mac2port = CacheTable(entry_duration=1000)
        self.ports = [
            Port(
                host=self,
                nic=nic,
                mac2port=self.mac2port,
                index=i,
            ) for i, nic in enumerate(self.nics)
        ]
        each(self.ports).calc_other_ports(self.ports)
        mint.worker(self.run, priority=simulation.SWITCH_PRIORITY)

    def run(self):
        while True:
            each(self.ports).forward()
            mint.elapse(1)

    # isinstance(at, Tip) == True
    # isinstance(at.master, NIC) == True
    def sending(self, at):
        return at.master.sending

    def sent(self, at):
        return at.master.sent

    @property
    def status(self):
        return [
            ('routes', self.mac2port),
        ]

class Port(object):

    def __init__(self, host, nic, mac2port, index):
        self.host = host
        self.nic = nic
        self.mac2port = mac2port
        self.index = index

    def calc_other_ports(self, ports):
        self.other_ports = [p for p in ports if p != self]

    def forward(self):
        try:
            raw = self.nic.recv(block=False)
            self.on_frame(raw)
        except Empty:
            pass

    def on_frame(self, raw):
        try:
            frame = Frame(raw)
        except UnknownFormat:
            self.host.report('{} got unknown type frame, ignored', self)
            return
        self.mac2port[frame.src_mac] = self
        self.host.report('{} <= {}', self, frame.src_mac)
        if frame.dst_mac in (frame.src_mac, MAC_Loopback):
            self.host.report('loopback frame, ignored')
            return
        try:
            port = self.mac2port[frame.dst_mac]
        except KeyError:
            self.flood(frame)
        else:
            self.host.report('{} -> {}', self.index, port.index)
            port.send(frame)

    def flood(self, frame):
        each(self.other_ports).send(frame)
        self.host.report(
            '{} -> {}',
            self.index,
            ','.join(map(str, each(self.other_ports).index)),
        )

    def send(self, frame):
        try:
            self.nic.send(frame.raw, block=False)
        except Full:
            self.host.report('drop frame on port-{}', self)

    def __str__(self):
        return 'port-{}'.format(self.index)
