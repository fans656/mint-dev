from mint import *
from f6 import each

a = Host()
b = Host(ip='192.168.0.1/24')
link(a, b)

from mint.protocols.dhcp import DHCPServer
b.dhcp_server = DHCPServer(b)
ips = IP.range('192.168.0.100', '192.168.0.254')
b.dhcp_server.pool.add(*ips)

run(gui=True, until=9999)
