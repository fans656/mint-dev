import simulation
from simulation import Simulation, sim
from components import Host, Switch, Router, Link
from components import link

import protocols

def wait(*args, **kwargs):
    return Simulation.sim.wait(*args, **kwargs)

def delegate(method_name):
    def f_(*args, **kwargs):
        f = getattr(simulation.Simulation.current_sim, method_name)
        return f(*args, **kwargs)
    return f_

for method_name in ('actor', 'run', 'process', 'add',
                    'elapse', 'put', 'worker'):
    exec '{} = delegate("{}")'.format(method_name, method_name)

report = put

def now():
    return Simulation.current_sim.now
