from collections import deque
import mint
from mint.pdus import (
    Frame, Packet, Datagram, Segment,
    IP, Port,
    IP_Loopback, IP_All,
)

class socket(object):

    class error(Exception): pass

    AF_INET = 0x04

    SOCK_DGRAM = 0x01
    SOCK_STREAM = 0x02

class LibSocket(object):

    AF_INET = socket.AF_INET
    SOCK_DGRAM = socket.SOCK_DGRAM
    SOCK_STREAM = socket.SOCK_STREAM

    def __init__(self, host):
        self.host = host

    def socket(self,
               family=socket.SOCK_STREAM,
               type=socket.SOCK_STREAM):
        if type == LibSocket.SOCK_DGRAM:
            Socket = UDPSocket
        elif type == LibSocket.SOCK_STREAM:
            Socket = TCPSocket
        else:
            raise socket.error('invalid type')
        return Socket(self.host, family, type)

class Socket(object):

    def __init__(self, host, family, type):
        self.host = host
        self.family = family
        self.type = type
        self.bound = False

    def bind(self, addr):
        ip, port = IP(addr[0]), Port(addr[1]) if addr[1] else None
        self.local_addr = self.host.bind(self, (ip, port))
        self.ip, self.port = self.local_addr
        self.bound = True

    def close(self):
        self.close_socket(self)

class UDPSocket(Socket):

    def __init__(self, *args, **kwargs):
        super(UDPSocket, self).__init__(*args, **kwargs)
        self.idata = deque() # UDP

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

    def feed(self, datagram, src_ip):
        self.idata.append((
            datagram.payload,
            (src_ip.user_form, datagram.src_port.user_form)
        ))

class TCPSocket(Socket):

    Initial = 0
    Listening = 1

    def __init__(self, *args, **kwargs):
        super(TCPSocket, self).__init__(*args, **kwargs)
        self.state = TCPSocket.Initial
        self.sockets = {}

    def listen(self, backlog):
        if not self.bound:
            raise socket.error('not bound')
        self.listening = True

    def connect(self, addr):
        ip, port = addr
        ip = IP(ip)
        port = Port(port)
        if not self.bound:
            self.bind((IP_All, None))
        segment = Segment(
            src_port=self.port,
            dst_port=port,
            syn=True,
        )
        self.host.send_ip(segment.raw, ip, protocol=Packet.Protocol.TCP)

    def feed(self, segment, src_ip):
        if self.state == TCPSocket.Initial:
            return
        if self.state == TCPSocket.Listening:
            src_port = segment.src_port
            src_addr = (src_ip, src_port)
            if src_addr not in self.sockets:
                self.sockets[src_addr] = LibSocket.socket()
            sock = self.sockets[src_addr]
            # TODO
