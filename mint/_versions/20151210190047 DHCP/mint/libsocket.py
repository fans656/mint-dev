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
        self.idata = deque() # UDP

        self.family = family
        self.type = type

    def bind(self, addr):
        ip, port = IP(addr[0]), Port(addr[1])
        self.local_addr = self.host.bind(self, (ip, port))
        self.ip, self.port = self.local_addr

    def sendto(self, data, addr):
        dst_ip, dst_port = addr
        self.host.send_udp(
            data,
            src_port=self.local_addr[1],
            dst_ip=dst_ip,
            dst_port=dst_port,
        )

    def recvfrom(self, bufsize=0):
        while True:
            try:
                return self.idata.popleft()
            except IndexError:
                mint.elapse(1)

    def feed_datagrams(self, datagram, src_ip):
        self.idata.append((
            datagram.payload,
            (src_ip.user_form, datagram.src_port.user_form)
        ))
