from mint import *

a, b = Host(), Host()
s = Switch()

link(a, s.tips[0], 1)
link(b, s.tips[1], 2)

a.send('hi')

start()
