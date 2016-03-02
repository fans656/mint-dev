from mint import *
from f6 import each

a = Host(ip='192.168.0.1/24')
b = Host(ip='192.168.0.2/24')
link(a, b)

a.interface.arp_table[b.ip] = b.mac

def client(socket):
    sock = socket.socket()
    sock.connect(('192.168.0.2', 80))
actor(client, a.libsocket)

def server(socket):
    lsock = socket.socket()
    lsock.bind(('0.0.0.0', 80))
    lsock.listen(5)
    #while True:
    #    sock, addr = lsock.accept()
    #    sock.host.report('accept {}', addr)
actor(server, b.libsocket)

run(gui=True, until=9999)
