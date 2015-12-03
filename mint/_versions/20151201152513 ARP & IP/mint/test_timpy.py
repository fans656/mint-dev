from timpy import *

@env.process()
def f():
    put(env.now, 'f init')

@env.process(daemon=True)
def f():
    while True:
        env.timeout(1)
        print 'hi'

print env.finished
env.step()
print env.finished
env.step()
print env.finished
#env.step()
#print env.
