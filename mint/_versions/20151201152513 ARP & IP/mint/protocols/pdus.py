import struct
from mint.utils import (mac_to_bytes, mac_from_bytes,
                        ip_from_str, ip_to_str)

class Raw(object):

    def __init__(self, raw):
        self.raw = raw
        self.i = 0

    def pop(self, n):
        b = self.i
        e = b + n
        self.i = e
        return self.raw[b:e]

    def popall(self):
        return self.pop(len(self.raw) - self.i)

class PDU(object):

    def __init__(self, raw=None, **kwargs):
        self.__i = 0
        if raw is None:
            raw = self.compose(**kwargs)
        self.raw = raw
        self.discompose(Raw(raw))

class Field(object):

    def __init__(self, **kwargs):
        self.name2value = kwargs
        self.value2name = {v: k for k, v in self.name2value.items()}
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __str__(self):
        s = ','.join('{}={}'.format(k, repr(v))
                     for k, v in self.name2value.items())
        return '<{}>'.format(s)

    def __getitem__(self, val):
        return self.value2name[val]

MAC = Field(
    Invalid='\x00',
    Broadcast='\xff',
)

class Frame(PDU):

    EtherType = Field(
        IPv4='\x01',
        ARP='\x02',
    )

    def discompose(self, raw):
        self.dst = raw.pop(1)
        self.src = raw.pop(1)
        self.ethertype = raw.pop(1)
        self.payload = raw.popall()

    def compose(self, dst, src, ethertype, payload):
        return dst + src + ethertype + payload

class Packet(PDU):

    Protocol = Field(
        Raw='\x00',
        TCP='\x01',
        UDP='\x02',
    )

    def discompose(self, raw):
        self.protocol = raw.pop(1)
        self.src = raw.pop(4)
        self.dst = raw.pop(4)
        self.payload = raw.popall()

    def compose(self, protocol, src, dst, payload):
        return protocol + src + dst + payload

class ARP(PDU):

    Oper = Field(
        WhoIs='\x01',
        IAm='\x02',
    )

    def discompose(self, raw):
        self.oper = raw.pop(1)
        self.src_ip = raw.pop(4)
        self.src_mac = raw.pop(1)
        self.dst_ip = raw.pop(4)
        self.dst_mac = raw.pop(1)

    def compose(self, oper, src_ip, src_mac, dst_ip, dst_mac):
        return oper + src_ip + src_mac + dst_ip + dst_mac

from collections import OrderedDict
class Discomposer(object):

    def __init__(self, getter):
        self.getter = getter

    @property
    def status(self):
        raw = self.getter()
        r = OrderedDict([('raw', repr(raw))])
        if raw:
            frame = Frame(raw)
            r['Frame'] = OrderedDict([
                ('Dst MAC', '{:02x}'.format(mac_from_bytes(frame.dst))),
                ('Src MAC', '{:02x}'.format(mac_from_bytes(frame.src))),
                ('EtherType', Frame.EtherType[frame.ethertype]),
            ])
            if frame.ethertype == Frame.EtherType.IPv4:
                packet = Packet(frame.payload)
                r['IPv4'] = OrderedDict([
                    ('Protocol', Packet.Protocol[packet.protocol]),
                    ('Src IP', ip_to_str(packet.src)),
                    ('Dst IP', ip_to_str(packet.dst)),
                    ('Payload', repr(packet.payload)),
                ])
            elif frame.ethertype == Frame.EtherType.ARP:
                arp = ARP(frame.payload)
                r['ARP'] = OrderedDict([
                    ('Oper', ARP.Oper[arp.oper]),
                    ('Src IP', ip_to_str(arp.src_ip)),
                    ('Src MAC', '{:02x}'.format(mac_from_bytes(arp.src_mac))),
                    ('Dst IP', ip_to_str(arp.dst_ip)),
                    ('Dst MAC', '{:02x}'.format(mac_from_bytes(arp.dst_mac))),
                ])
        return r
