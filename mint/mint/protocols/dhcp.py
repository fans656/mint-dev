import struct
from collections import OrderedDict, deque

import mint
from mint import Signal
from mint.protocols import Protocol
from mint.pdus import (
    IP, MAC,
    IP_All, IP_Invalid, IP_Broadcast,
    PDU, Field
)

class DHCP(Protocol):

    def __init__(self, host):
        super(DHCP, self).__init__(host)
        self.report = self.host.report
        self.socket = self.host.libsocket
        mint.process(self.run)

    def discover(self):
        self.report('DHCP Discover')
        pdu = DHCP.PDU(
            # yiaddr (your ip address)
            IP_Invalid,
            # siaddr (server ip address)
            IP_Invalid,
            # chaddr (client hardware address)
            self.host.mac,
            # message type
            DHCP.Opt.MessageType, 1, DHCP.Opt.Ext.MessageType.Discover,
            # end
            DHCP.Opt.End,
        )
        self.sock.sendto(pdu.raw, (IP_Broadcast, DHCP.ServerPort))

    def offer(self, ip, discover):
        self.report('DHCP Offer {}', ip)
        pdu = DHCP.PDU(
            # yiaddr (your ip address)
            ip,
            # siaddr (server ip address)
            self.sock.ip,
            # chaddr (client hardware address)
            discover.chaddr,
            # message type
            DHCP.Opt.MessageType, 1, DHCP.Opt.Ext.MessageType.Offer,
            # end
            DHCP.Opt.End,
        )
        self.sock.sendto(pdu.raw, (IP_Broadcast, DHCP.ClientPort))

    def request(self, offer):
        self.report('DHCP Request {}', offer.yiaddr)
        pdu = DHCP.PDU(
            # yiaddr (your ip address)
            IP_Invalid,
            # siaddr (server ip address)
            offer.siaddr,
            # chaddr (client hardware address)
            self.host.mac,
            # options
            DHCP.Opt.MessageType, 1, DHCP.Opt.Ext.MessageType.Request,
            DHCP.Opt.RequestedIP, 4, offer.yiaddr.bytes_form,
            # end
            DHCP.Opt.End,
        )
        self.sock.sendto(pdu.raw, (IP_Broadcast, DHCP.ServerPort))

    def ack(self, request):
        self.report('DHCP Ack {}', request.options['RequestedIP'])
        routers = [IP(ip).bytes_form for ip in self.routers]
        pdu = DHCP.PDU(
            # yiaddr (your ip address)
            request.options['RequestedIP'],
            # siaddr (server ip address)
            self.sock.ip,
            # chaddr (client hardware address)
            request.chaddr,
            # options
            DHCP.Opt.MessageType, 1, DHCP.Opt.Ext.MessageType.Ack,
            DHCP.Opt.SubnetMask, 4, self.subnet_mask.bytes_form,
            DHCP.Opt.Router, 4 * len(routers), ''.join(routers),
            DHCP.Opt.LeaseTime, 4, struct.pack('!I', self.lease_time),
            # end
            DHCP.Opt.End,
        )
        self.sock.sendto(pdu.raw, (IP_Broadcast, DHCP.ClientPort))

    ServerPort = 67
    ClientPort = 68

    class Opt(object):

        SubnetMask = struct.pack('!B', 1)
        Router = struct.pack('!B', 3)
        LeaseTime = struct.pack('!B', 51)
        RequestedIP = struct.pack('!B', 50)
        MessageType = struct.pack('!B', 53)
        ServerIdentifier = struct.pack('!B', 54)
        End = struct.pack('!B', 255)

        class Ext(object):

            MessageType = Field(
                Discover = '\x01',
                Offer = '\x02',
                Request = '\x03',
                Ack = '\x05',
            )

    class PDU(PDU):

        def discompose(self, raw):
            self.yiaddr = IP.from_bytes(raw.pop(4))
            self.siaddr = IP.from_bytes(raw.pop(4))
            self.chaddr = MAC.from_bytes(raw.pop(1))
            self.options = OrderedDict()
            while True:
                opt = raw.pop(1)
                if opt == DHCP.Opt.End:
                    break
                length = struct.unpack('!B', raw.pop(1))[0]
                content = raw.pop(length)
                if opt == DHCP.Opt.MessageType:
                    message_type = DHCP.Opt.Ext.MessageType[content]
                    self.options['MessageType'] = message_type
                    self.MessageType = message_type
                elif opt == DHCP.Opt.RequestedIP:
                    self.options['RequestedIP'] = IP.from_bytes(content)
                elif opt == DHCP.Opt.ServerIdentifier:
                    self.options['ServerIdentifier'] = IP.from_bytes(content)
                elif opt == DHCP.Opt.SubnetMask:
                    self.options['SubnetMask'] = IP.from_bytes(content)
                elif opt == DHCP.Opt.Router:
                    ips = [content[i:i+4] for i in xrange(0, len(content), 4)]
                    self.options['Router'] = map(IP.from_bytes, ips)
                elif opt == DHCP.Opt.LeaseTime:
                    self.options['LeaseTime'] = struct.unpack('!I', content)[0]

        def compose(self, yiaddr, siaddr, chaddr, *opts):
            r = ''
            r += IP(yiaddr)
            r += IP(siaddr)
            r += MAC(chaddr)
            opts = list(opts)
            for i, opt in enumerate(opts):
                if isinstance(opt, int):
                    opts[i] = struct.pack('!B', opt)
                elif not isinstance(opt, str):
                    opts[i] = str(opt)
            r += ''.join(opts)
            return r

class DHCPClient(DHCP):

    def run(self):
        if self.host.ip:
            return
        socket = self.socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock = self.sock
        sock.bind((IP_All, DHCP.ClientPort))
        self.discover()
        offers = self.collect_offers()
        offer = offers[0]
        self.request(offer)
        pdu = self.get_ack()
        self.host.ip = pdu.yiaddr
        self.host.mask = pdu.options['SubnetMask']
        self.host.default_gateway = pdu.options['Router'][0]

    def collect_offers(self):
        sock = self.sock
        offers = []
        while True:
            raw, (ip, port) = sock.recvfrom(4096)
            if port != DHCP.ServerPort:
                continue
            pdu = DHCP.PDU(raw)
            if pdu.options['MessageType'] != 'Offer':
                continue
            if pdu.chaddr != self.host.mac:
                self.report('offer for {} (i am {})',
                            pdu.chaddr, self.host.mac)
                continue
            offers.append(pdu)
            break
        return offers

    def get_ack(self):
        sock = self.sock
        while True:
            raw, (ip, port) = sock.recvfrom(4096)
            if port != DHCP.ServerPort:
                continue
            pdu = DHCP.PDU(raw)
            if pdu.options['MessageType'] != 'Ack':
                continue
            if pdu.chaddr != self.host.mac:
                continue
            break
        return pdu

class DHCPServer(DHCP):

    def __init__(self, host):
        super(DHCPServer, self).__init__(host)
        self.pool = Pool()
        self.subnet_mask = IP('0.0.0.0')
        self.routers = ['0.0.0.0']
        self.lease_time = 8000

    def run(self):
        socket = self.socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock = self.sock
        sock.bind((IP_All, DHCP.ServerPort))
        while True:
            raw, (ip, port) = sock.recvfrom(4096)
            if port != 68:
                continue
            pdu = DHCP.PDU(raw)
            msg_type = pdu.options['MessageType']
            if msg_type == 'Discover':
                try:
                    ip = self.pool.pick()
                    self.offer(ip, pdu)
                except KeyError:
                    self.report('no available ip')
            elif msg_type == 'Request':
                if pdu.siaddr == sock.ip:
                    self.ack(pdu)
                else:
                    self.report('put back offered ip')

class Pool(object):

    def __init__(self):
        self.ips = deque()

    def add(self, *ips):
        self.ips.extend(map(IP, ips))
    put_back = add

    def pick(self):
        return self.ips.popleft()
