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
)

class Switch(Entity):

    def __init__(self, n_tips=3):
        super(Switch, self).__init__(n_tips)
        self.nics = [NIC(tip) for tip in self.tips]
        mac2port = CacheTable(entry_duration=1000)
        self.ports = [
            Port(
                host=self,
                nic=nic,
                mac2port=mac2port,
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
        frame = Frame(raw)
        self.mac2port[frame.src_mac] = self
        if frame.dst_mac in (frame.src_mac, MAC_Loopback):
            return
        try:
            port = self.mac2port[frame.dst_mac]
        except KeyError:
            self.flood(frame)
        else:
            port.send(frame)

    def flood(self, frame):
        each(self.other_ports).send(frame)

    def send(self, frame):
        try:
            self.nic.send(frame.raw, block=False)
        except Full:
            self.host.report('drop frame on port-{}', self.index)
