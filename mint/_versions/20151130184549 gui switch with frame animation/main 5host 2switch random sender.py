import random
from mint import *
from mint.exceptions import Empty

def send(sender):
    while True:
        if random.choice([0,3]) == 0:
            sender.send('\xff', random.choice(hosts).mac)
        elapse(random.randint(50, 80))
        try:
            sender.framer.recv(block=False)
        except Empty:
            pass

a, b, c = Host(), Host(), Host()
d, e = Host(), Host()
hosts = (a,b,c,d,e)
for host in hosts:
    actor(send, host)

s1, s2 = Switch(n_tips=4), Switch()

link(a, s1.tips[0])
link(b, s1.tips[1])
link(c, s1.tips[2])

link(d, s2.tips[0])
link(e, s2.tips[1])

link(s1.tips[3], s2.tips[2])

run(gui=True)
