'''
UDP 1-server & 2-clients

a is the server.
b and c is the client.

first b want to send datagram to a
so it performs the arp.

c at 200 do the same.

with arp performed, b and c sends datagrams to a.
a sends respond datagram to client,
note that it need not to do arp
because the receiving datagram tell the peer's ip & mac.
'''
from mint import *

a, b, c = Host(), Host(), Host()
a.arp_table[b.ip] = b.mac
s = Switch()
link(a, s.tips[0])
link(b, s.tips[1])
link(c, s.tips[2])

def server(socket):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('', 80))
    while True:
        msg, addr = sock.recvfrom()
        put('{} | Message from {}: {}'.format(
            sock.getsockname(),
            addr, repr(msg)
        ))
        sock.sendto('hi, you said: {}'.format(msg), addr)
actor(server, a.libsocket)

server_addr = (a.ip, 80)

def sender(socket, server_addr):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('', 6560))
    sock.sendto('hi, i\'m {}'.format(sock.getsockname()), server_addr)
    msg, addr = sock.recvfrom()
    put('server at {} said: {}', addr, repr(msg))
actor(sender, b.libsocket, server_addr)

def sender2(socket, server_addr):
    elapse(200)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('', 6560))
    sock.sendto('hi, i\'m {}'.format(sock.getsockname()), server_addr)
    msg, addr = sock.recvfrom()
    put('{} | server at {} said: {}',
        sock.getsockname(),
        addr, repr(msg))
actor(sender2, c.libsocket, server_addr)

run(gui=True, until=2571)
