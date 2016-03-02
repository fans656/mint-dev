from mint import *

a, b = Host(), Host()
link(a, b, 5)

a.send('hi').at(5)
b.send('me').at(0)

start()
