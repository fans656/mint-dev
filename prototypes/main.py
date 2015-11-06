'''
Utopia simplex protocol
'''
from mint import *
from devices import PC

@proc
def _():
    for line in open('main.py'):
        a.send(line)

@proc
def _():
    while True:
        line = ''
        while True:
            ch = b.recv(1)
            if ch == '\n':
                break
            line += ch
        put('{:10}'.format(now()), b, line)

def debug():
    put(now(), phase())
    a.port.show()
    b.port.show()
    raw_input()

a, b = PC('a'), PC('b')
link(a, b)
run()
