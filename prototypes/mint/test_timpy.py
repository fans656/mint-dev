from timpy import *

@env.process(priority=0)
def f():
    put(env.now, 'f init')
    pass

@env.process(priority=0)
def g():
    put(env.now, 'g init')
    env.timeout(2)
    put(env.now, 'g timeout 2')

@env.process(priority=1)
def h():
    put(env.now, 'h init')
    env.timeout(1)
    put(env.now, 'h timeout 1')
    env.timeout(1)
    put(env.now, 'h timeout 1 again')

while not env.finished:
    env.step(by=env.Priority)
    raw_input()
