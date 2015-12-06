from mint import *
from mint.pdus import Packet
from f6 import each

a = Host(ip='192.168.0.2')
b = Host(ip='192.168.0.3')
c = Host(ip='10.0.0.2')
s = Switch()
r = Router()

r[0].ip = '192.168.0.1/24'
r[1].ip = '10.0.0.1/24'
r.routes.add('192.168.0.0', '255.255.255.0', '0.0.0.0', r[0])
r.routes.add('10.0.0.0', '255.255.255.0', '0.0.0.0', r[1])

each((a,b)).default_gateway = '192.168.0.1'
c.default_gateway = '10.0.0.1'

link(a, s)
link(b, s)
link(s, r)
link(r, c)

a.interface.arp_table[b.ip] = b.mac

@actor
def _():
    #a.send('hi', ip='192.168.0.3')
    a.send('hi', ip='10.0.0.2')
    #a.send('hi', ip='9.9.9.9')

run(gui=True, until=9999)
