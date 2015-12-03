import struct

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
        s = ','.join('{}={}'.format(k, str(v))
                     for k, v in self.name2value.items())
        return '<{}>'.format(s)

    def __getitem__(self, val):
        return self.value2name[val]

class Frame(PDU):

    EtherType = Field(
        Raw='\x00',
        IPv4='\x01',
        ARP='\x02',
    )

    def discompose(self, raw):
        self.dst_mac = mac_from_bytes(raw.pop(1))
        self.src_mac = mac_from_bytes(raw.pop(1))
        self.ethertype = raw.pop(1)
        self.payload = raw.popall()

    def compose(self, dst_mac, src_mac, ethertype, payload):
        #assert isinstance(dst_mac, MAC)
        #assert isinstance(src_mac, MAC)
        return dst_mac + src_mac + ethertype + payload

class Packet(PDU):

    Protocol = Field(
        Raw='\x00',
        TCP='\x01',
        UDP='\x02',
    )

    def discompose(self, raw):
        self.protocol = raw.pop(1)
        self.src_ip = ip_from_bytes(raw.pop(4))
        self.dst_ip = ip_from_bytes(raw.pop(4))
        self.payload = raw.popall()

    def compose(self, protocol, src_ip, dst_ip, payload):
        #assert isinstance(src_ip, IP)
        #assert isinstance(dst_ip, IP)
        return protocol + src_ip + dst_ip + payload

class Datagram(PDU):

    def discompose(self, raw):
        self.src_port = port_from_bytes(raw.pop(2))
        self.dst_port = port_from_bytes(raw.pop(2))
        self.payload = raw.popall()

    def compose(self, src_port, dst_port, payload):
        #assert isinstance(src_port, Port)
        #assert isinstance(dst_port, Port)
        return src_port + dst_port + payload

class ARP(PDU):

    Oper = Field(
        WhoIs='\x01',
        IAm='\x02',
    )

    def discompose(self, raw):
        self.oper = raw.pop(1)
        self.src_ip = ip_from_bytes(raw.pop(4))
        self.src_mac = mac_from_bytes(raw.pop(1))
        self.dst_ip = ip_from_bytes(raw.pop(4))
        self.dst_mac = mac_from_bytes(raw.pop(1))

    def compose(self, oper, src_ip, src_mac, dst_ip, dst_mac):
        return oper + src_ip + src_mac + dst_ip + dst_mac

class Bytes(object):

    def __init__(self, val=None):
        if val is not None:
            self.user_form = val
            self.bytes_form = self.from_user_form(val)

    @classmethod
    def from_bytes(cls, val):
        return cls(cls.to_user_form(val))

    def __repr__(self):
        return str(self)
        return '{}({})'.format(type(self).__name__, self.user_form)

    def __add__(self, o):
        return self.bytes_form + o

    def __radd__(self, o):
        return o + self.bytes_form

    def __eq__(self, o):
        return self.bytes_form == o.bytes_form

    def __ne__(self, o):
        return not self == o

    def __hash__(self):
        return hash(self.bytes_form)

class IP(Bytes):

    @staticmethod
    def from_user_form(ip):
        # e.g. '1.2.3.4' -> '\x00\x00\x00\x01...'
        if ip == '':
            ip = str(IP_All)
        elif ip == 'localhost':
            ip = str(IP_Loopback)
        return struct.pack('!4B', *map(int, ip.split('.')))

    @staticmethod
    def to_user_form(bytes):
        # e.g. '\x00\x00\x00\x01...' -> '1.2.3.4'
        return '.'.join(map(str, struct.unpack('!4B', bytes)))

    def __str__(self):
        return self.user_form

IP_Loopback = IP('127.0.0.1')
IP_All = IP('0.0.0.0')

class Port(Bytes):

    @staticmethod
    def from_user_form(port):
        # e.g. 6560 -> '\x19\xa0'
        return struct.pack('!H', port)

    @staticmethod
    def to_user_form(bytes):
        # e.g. '\x19\xa0' -> 6560
        return struct.unpack('!H', bytes)[0]

    def __str__(self):
        return str(self.user_form)

    def __int__(self):
        return self.user_form

class MAC(Bytes):

    @staticmethod
    def from_user_form(val):
        # e.g. 0x01 -> '\x01'
        return struct.pack('!B', val)

    @staticmethod
    def to_user_form(val):
        # e.g. '\x01' -> 0x01
        return struct.unpack('!B', val)[0]

    def __str__(self):
        return '{:02x}'.format(self.user_form)

    def __int__(self):
        return self.user_form

MAC_Invalid = MAC(0x00)
MAC_Loopback = MAC(0xf1)
MAC_Broadcast = MAC(0xff)

def ip_from_user(val):
    return IP(val)

def ip_from_bytes(val):
    return IP.from_bytes(val)

def port_from_user(val):
    return Port(val)

def port_from_bytes(val):
    return Port.from_bytes(val)

def mac_from_user(val):
    return MAC(val)

def mac_from_bytes(val):
    return MAC.from_bytes(val)

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
                ('Dst MAC', str(frame.dst_mac)),
                ('Src MAC', str(frame.src_mac)),
                ('EtherType', Frame.EtherType[frame.ethertype]),
            ])
            if frame.ethertype == Frame.EtherType.IPv4:
                packet = Packet(frame.payload)
                r['IPv4'] = OrderedDict([
                    ('Protocol', Packet.Protocol[packet.protocol]),
                    ('Src IP', str(packet.src_ip)),
                    ('Dst IP', str(packet.dst_ip)),
                ])
                if packet.protocol == Packet.Protocol.UDP:
                    datagram = Datagram(packet.payload)
                    r['UDP'] = OrderedDict([
                        ('Src Port', str(datagram.src_port)),
                        ('Dst Port', str(datagram.dst_port)),
                        ('Payload', repr(datagram.payload)),
                    ])
            elif frame.ethertype == Frame.EtherType.ARP:
                arp = ARP(frame.payload)
                r['ARP'] = OrderedDict([
                    ('Oper', ARP.Oper[arp.oper]),
                    ('Src IP', str(arp.src_ip)),
                    ('Src MAC', str(arp.src_mac)),
                    ('Dst IP', str(arp.dst_ip)),
                    ('Dst MAC', str(arp.dst_mac)),
                ])
        return r
