env = Environment()

@env.proc
def _():
    a.send('hi')
    print a.recv()

@env.proc
def _():
    s = b.recv()
    b.send('you said "' + s + '"')

a, b = Host(), Host()
