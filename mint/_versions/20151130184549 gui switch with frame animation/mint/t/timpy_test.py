import time
from timpy import *

@env.priority(0)
def f():
    env.timeout(20)
    put(env.now, 'f')
    time.sleep(0.5)

@env.priority(1)
def g():
    f.wait()
    env.timeout(3)
    put(env.now, 'g')

ok = env.event()
env.run()
