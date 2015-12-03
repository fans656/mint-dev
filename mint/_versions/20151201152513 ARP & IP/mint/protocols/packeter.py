from collections import defaultdict

import mint
from mint.utils import ip_to_str
from mint.protocols.pdus import Frame, Packet, ARP, MAC

class Packeter(object):

    def __init__(self, framer, ip):
        framer.handlers = {
            Frame.EtherType.IPv4: self.on_ipv4,
            Frame.EtherType.ARP: self.on_arp,
        }
        self.framer = framer
        self.ip = ip
        self.arp_cache = {}
        self.pending_packets = defaultdict(lambda: [])

    def send(self, data, to, protocol):
        dst_ip = to
        packet = Packet(
            protocol=protocol,
            src=self.ip,
            dst=dst_ip,
            payload=data,
        )
        try:
            dst_mac = self.arp_cache[dst_ip][0]
        except KeyError:
            self.pending_packets[dst_ip].append(packet)
            self.query_mac_of(dst_ip)
        else:
            self.framer.send(packet.raw, to=dst_mac)

    def query_mac_of(self, ip):
            packet = ARP(
                oper=ARP.Oper.WhoIs,
                src_ip=self.ip,
                src_mac=self.framer.mac,
                dst_ip=ip,
                dst_mac=MAC.Invalid,
            ).raw
            self.framer.send(
                packet,
                to=MAC.Broadcast,
                ethertype=Frame.EtherType.ARP
            )

    def on_ipv4(self, raw):
        packet = Packet(raw)
        mint.report('{} recved {}'.format(
            ip_to_str(self.ip),
            repr(packet.payload),
        ))

    def on_arp(self, raw):
        arp = ARP(raw)
        if arp.oper == ARP.Oper.IAm:
            mint.report('{} got ARP annoucement from {}'.format(
                ip_to_str(self.ip),
                ip_to_str(arp.src_ip),
            ))
            self.arp_cache[arp.src_ip] = (arp.src_mac, mint.now())
            packets = self.pending_packets[arp.src_ip]
            for packet in packets:
                self.framer.send(packet.raw, arp.src_mac)
            del packets[:]
        elif arp.oper == ARP.Oper.WhoIs:
            if not arp.dst_ip == self.ip:
                mint.report('{} got irrelevant ARP packet'.format(
                    ip_to_str(self.ip)
                ))
                return
            packet = ARP(
                oper=ARP.Oper.IAm,
                src_ip=self.ip,
                src_mac=self.framer.mac,
                dst_ip=arp.src_ip,
                dst_mac=arp.src_mac,
            ).raw
            self.framer.send(
                packet,
                to=arp.src_mac,
                ethertype=Frame.EtherType.ARP,
            )
