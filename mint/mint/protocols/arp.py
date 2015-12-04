from mint.protocols import Protocol, Signal
from mint.cachetable import CacheTable
from mint.pdus import (
    ARP as PDU,
    Frame,
    IP_Loopback,
    MAC_Invalid, MAC_Broadcast,
)

class ARP(Protocol):

    DelegatedAttributes = Protocol.DelegatedAttributes | set([
        'pending_packets',
    ])

    updated = Signal()

    def __init__(self, host):
        super(ARP, self).__init__(host)
        self.ip2mac = CacheTable(entry_duration=1000)

    def process(self, raw):
        pdu = PDU(raw)
        self.ip2mac[pdu.src_ip] = pdu.src_mac
        if pdu.oper == PDU.Oper.IAm:
            self.update(pdu)
            return
        if pdu.dst_ip != self.ip:
            self.report(
                'got irrelevent request for {} (i\'m {})',
                pdu.dst_ip, self.ip)
            return
        if pdu.oper == PDU.Oper.WhoIs:
            self.respond(pdu)
            return

    def update(self, respond):
        ip, mac = respond.src_ip, respond.src_mac
        self.report('oh, {} is {}', mac, ip)
        self.ip2mac[ip] = mac
        self.updated.emit(ip, mac)

    def query(self, dst_ip):
        pdu = PDU(
            oper=PDU.Oper.WhoIs,
            src_ip=self.ip,
            src_mac=self.mac,
            dst_ip=dst_ip,
            dst_mac=MAC_Invalid,
        )
        frame = Frame(
            dst_mac=MAC_Broadcast,
            src_mac=self.mac,
            ethertype=Frame.EtherType.ARP,
            payload=pdu.raw,
        )
        self.send_frame(frame)
        self.report('ask who is', pdu.dst_ip)

    def respond(self, request):
        pdu = PDU(
            oper=PDU.Oper.IAm,
            src_ip=self.ip,
            src_mac=self.mac,
            dst_ip=request.src_ip,
            dst_mac=request.src_mac,
        )
        frame = Frame(
            dst_mac=request.src_mac,
            src_mac=self.mac,
            ethertype=Frame.EtherType.ARP,
            payload=pdu.raw,
        )
        self.send_raw(frame.raw)
        self.report(
            'tell {} that {} is {}',
            pdu.dst_ip, pdu.src_mac, pdu.src_ip,
        )
