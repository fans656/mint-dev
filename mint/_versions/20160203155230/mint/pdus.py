import struct, traceback
from bitarray import bitarray

class PDU(object):

    def __init__(self, raw=None, *args, **kwargs):
        self.__i = 0
        if args and kwargs:
            raise ValueError('PDU with args and kwargs')
        if kwargs:
            raw = self.compose(**kwargs)
        elif args:
            raw = self.compose(raw, *args)
        self.raw = raw
        try:
            self.discompose(Raw(raw))
        except IndexError:
            traceback.print_exc()
            raise BadFormat(type(self).__name__)

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

class Data(PDU):

    def discompose(self, raw):
        self.payload = raw.popall()

    def compose(self, payload):
        return payload

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
        self.src_port = Port(raw.pop(2))
        self.dst_port = Port(raw.pop(2))
        self.payload = raw.popall()

    def compose(self, src_port, dst_port, payload):
        return src_port + dst_port + payload

class Segment(PDU):

    IDX_ACK = 3
    IDX_SYN = 6
    IDX_FIN = 7

    def discompose(self, raw):
        self.src_port = Port.from_bytes(raw.pop(2))
        self.dst_port = Port.from_bytes(raw.pop(2))
        flags = bitarray()
        flags.frombytes(raw.pop(1))
        self.ack = flags[Segment.IDX_ACK]
        self.syn = flags[Segment.IDX_SYN]
        self.fin = flags[Segment.IDX_FIN]
        self.payload = raw.popall()

    def compose(self,
                src_port,
                dst_port,
                syn=False,
                ack=False,
                fin=False,
                payload='',
                ):
        flags = bitarray('0' * 8)
        flags[Segment.IDX_ACK] = ack
        flags[Segment.IDX_SYN] = syn
        flags[Segment.IDX_FIN] = fin
        flags = flags.tobytes()
        return src_port + dst_port + flags + payload

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

    def __init__(self, val):
        if isinstance(val, Bytes):
            self.user_form = val.user_form
            self.bytes_form = val.bytes_form
        else:
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
    def range(beg, end):
        beg, end = IP(beg), IP(end)
        return map(IP.from_int, range(int(beg), int(end) + 1))

    def __init__(self, val):
        super(IP, self).__init__(val)
        bits = bitarray()
        bits.frombytes(self.bytes_form)
        self.bits_form = bits

    @staticmethod
    def from_user_form(ip):
        # e.g. '1.2.3.4' -> '\x00\x00\x00\x01...'
        if ip == '':
            ip = str(IP_All)
        elif ip == 'localhost':
            ip = str(IP_Loopback)
        return struct.pack('!4B', *map(int, ip.split('.')))

    @staticmethod
    def from_int(i):
        return IP.from_bytes(struct.pack('!I', i))

    @staticmethod
    def to_user_form(bytes):
        # e.g. '\x00\x00\x00\x01...' -> '1.2.3.4'
        return '.'.join(map(str, struct.unpack('!4B', bytes)))

    @staticmethod
    def from_bits(bits):
        return IP.from_bytes(bits.tobytes())

    @property
    def net_len(self):
        # for subnet mask, the # of 1s is just the CIDR prefix length
        return self.bits_form.count(1)

    def __str__(self):
        return self.user_form

    def __and__(self, o):
        return IP.from_bits(self.bits_form & o.bits_form)

    def __int__(self):
        return struct.unpack('!I', self.bytes_form)[0]

    def __nonzero__(self):
        return self != IP_All

IP_Loopback = IP('127.0.0.1')
IP_Broadcast = IP('255.255.255.255')
IP_All = IP('0.0.0.0')
IP_Invalid = IP_All

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

    def __eq__(self, o):
        return self.user_form == Port(o).user_form

    def __ne__(self, o):
        return not self == o

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

class BadFormat(Exception): pass

class Raw(object):

    def __init__(self, raw):
        self.raw = raw
        self.i = 0

    def pop(self, n):
        b = self.i
        e = b + n
        self.i = e
        r = self.raw[b:e]
        if not r:
            raise IndexError('data empty ({}:{})'.format(b, e))
        return r

    def popall(self):
        try:
            return self.pop(len(self.raw) - self.i)
        except IndexError:
            return ''

    def __repr__(self):
        return repr(self.raw)

from collections import OrderedDict
class Discomposer(object):

    def __init__(self, getter):
        self.getter = getter

    @property
    def status(self):
        raw = self.getter()
        r = OrderedDict([('raw', repr(raw))])
        if raw:
            try:
                self.dis_frame(r, raw)
            except Exception:
                traceback.print_exc()
        return r

    def dis_frame(self, r, raw):
        frame = Frame(raw)
        r['Ethernet'] = OrderedDict([
            ('Dst MAC', str(frame.dst_mac)),
            ('Src MAC', str(frame.src_mac)),
            ('EtherType', Frame.EtherType[frame.ethertype]),
        ])
        if frame.ethertype == Frame.EtherType.IPv4:
            self.dis_ipv4(r, frame.payload)
        elif frame.ethertype == Frame.EtherType.ARP:
            self.dis_arp(r, frame.payload)

    def dis_ipv4(self, r, raw):
        packet = Packet(raw)
        r['IPv4'] = OrderedDict([
            ('Protocol', Packet.Protocol[packet.protocol]),
            ('Src IP', str(packet.src_ip)),
            ('Dst IP', str(packet.dst_ip)),
        ])
        if packet.protocol == Packet.Protocol.Raw:
            r['IPv4']['Payload'] = repr(packet.payload)
        elif packet.protocol == Packet.Protocol.UDP:
            self.dis_udp(r, packet.payload)
        elif packet.protocol == Packet.Protocol.TCP:
            self.dis_tcp(r, packet.payload)

    def dis_udp(self, r, raw):
        datagram = Datagram(raw)
        r['UDP'] = OrderedDict([
            ('Src Port', str(datagram.src_port)),
            ('Dst Port', str(datagram.dst_port)),
        ])
        if is_dhcp(datagram):
            self.dis_dhcp(r, datagram.payload)
        else:
            r['UDP']['Payload'] = repr(datagram.payload)

    def dis_tcp(self, r, raw):
        segment = Segment(raw)
        r['TCP'] = OrderedDict([
            ('Src Port', str(segment.src_port)),
            ('Dst Port', str(segment.dst_port)),
            ('Syn', segment.syn),
            ('Ack', segment.ack),
            ('Fin', segment.fin),
        ])
        r['TCP']['Payload'] = repr(segment.payload)

    def dis_dhcp(self, r, raw):
        from mint.protocols import DHCP
        dhcp = DHCP.PDU(raw)
        name = 'DHCP {}'.format(dhcp.options.pop('MessageType'))
        r[name] = OrderedDict([
            ('Your IP', dhcp.yiaddr),
            ('Server IP', dhcp.siaddr),
            ('Client MAC', dhcp.chaddr),
        ])
        r[name].update(dhcp.options)

    def dis_arp(self, r, raw):
        arp = ARP(raw)
        r['ARP'] = OrderedDict([
            ('Oper', ARP.Oper[arp.oper]),
            ('Src IP', str(arp.src_ip)),
            ('Src MAC', str(arp.src_mac)),
            ('Dst IP', str(arp.dst_ip)),
            ('Dst MAC', str(arp.dst_mac)),
        ])

def is_dhcp(datagram):
    src, dst = datagram.src_port, datagram.dst_port
    ports = (67, 68)
    return src in ports or dst in ports

if __name__ == '__main__':
    ip = IP('192.168.255.3')
    mask = IP('255.255.240.0')
    print ip & mask
