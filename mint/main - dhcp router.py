from mint import *

a = Host()
b = Host(ip='192.168.0.1/24')
c = Host()
s = Switch()
r = Router()

link(a, s)
link(b, s)
link(s, r)
link(r, c)

from mint.protocols.dhcp import DHCPServer
b.dhcp_server = DHCPServer(b)
ips = IP.range('192.168.0.100', '192.168.0.254')
b.dhcp_server.pool.add(*ips)

run(gui=True, until=9999)
