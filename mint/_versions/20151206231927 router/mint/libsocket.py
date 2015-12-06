from collections import deque
import mint
from mint.pdus import (
    Frame, Datagram, Packet,
    IP, ip_from_user,
    Port, port_from_user,
    IP_Loopback, IP_All,
)

class socket(object):

    class error(Exception): pass

class LibSocket(object):

    AF_INET = 0x04

    SOCK_DGRAM = 0x02

    def __init__(self, host):
        self.host = host

    def socket(self, family, type):
        return Socket(self.host, family, type)

class Socket(object):

    def __init__(self, host, family, type):
        self.host = host
        self.idatagrams = deque() # UDP

        self.family = family
        self.type = type

    def bind(self, addr):
        ip, port = canonicalized_addr(addr)
        self.local_addr = self.host.bind(self, ip, port)
        self.ip, self.port = self.local_addr

    def sendto(self, data, addr):
        addr = canonicalized_addr(addr)
        dst_ip, dst_port = addr
        if not self.local_addr:
            local_ip = IP_Loopback if dst_ip == IP_Loopback else IP_All
            self.bind((local_ip, None))
        datagram = Datagram(
            src_port=self.port,
            dst_port=dst_port,
            payload=data,
        )
        packet = Packet(
            protocol=Packet.Protocol.UDP,
            src_ip=self.ip,
            dst_ip=dst_ip,
            payload=datagram.raw,
        )
        self.host.send_packet(packet, ethertype=Frame.EtherType.IPv4)

    def recvfrom(self, bufsize=0):
        while True:
            try:
                data, (ip, port) = self.idatagrams.popleft()
                ip = str(ip)
                port = int(port)
                return data, (ip, port)
            except IndexError:
                mint.elapse(1)

    def getsockname(self):
        try:
            return self.local_addr
        except AttributeError:
            raise socket.error('socket has not been binded yet')

    def feed_datagram(self, data, addr):
        self.idatagrams.append((data, addr))

def canonicalized_addr(addr):
    ip, port = addr
    ip = canonicalized_ip(ip)
    port = canonicalized_port(port)
    return (ip, port)

def canonicalized_ip(ip):
    if isinstance(ip, str):
        return ip_from_user(ip)
    elif isinstance(ip, IP):
        return ip
    else:
        raise TypeError('unsupported ip form')

def canonicalized_port(port):
    if isinstance(port, int):
        return port_from_user(port)
    elif isinstance(port, Port):
        return port
    elif port is None:
        return None
    else:
        raise TypeError('unsupported port form')
