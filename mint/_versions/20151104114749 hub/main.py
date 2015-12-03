'''
3 hosts connected to 1 hub
the hub will determine a port's outgoing bit by
bitwise OR other ports incoming bits

host1 send '1'
host2 send '001'

<Host 0> received 00000100 at 8
<Host 1> received 00010000 at 8
<Host 2> received 00010100 at 8

==================================

seems like every entity in the path will introduce 1 tik-tok delay

run_2hosts_1link    - 01000000
    entities: link
run_2hosts_1hub     - 00010000
    entities: link -> hub -> link
run_2hosts_2hub     - 00000010
    entities: link -> hub1 -> link -> hub2
'''
from mint import *

@proc
def _():
    hosts[0].port.send('1')
    hosts[1].port.send('001')

def receiver(entity, nbits):
    data = entity.port.recv(nbits)
    print '{} received {} at {}\n'.format(entity, data, now())
    stop()

n_hosts = 3

hosts = [Host() for _ in range(n_hosts)]
hub = Hub(n_ports=n_hosts)
for host, port in zip(hosts, hub.ports):
    link(host, port)
for host in hosts:
    proc(receiver, host, 8)

run()
