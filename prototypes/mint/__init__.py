import simulation
from simulation import Simulation, sim
from components import Host, Link
from components import link
from utils import put

def wait(*args, **kwargs):
    return Simulation.sim.wait(*args, **kwargs)

def delegate(method_name):
    def f_(*args, **kwargs):
        f = getattr(simulation.Simulation.current_sim, method_name)
        return f(*args, **kwargs)
    return f_

for method_name in ('actor', 'run', 'process', 'add', 'elapse'):
    exec '{} = delegate("{}")'.format(method_name, method_name)

#def current_sim():
#    return Simulation.current_sim
#
def now():
    return current_sim().now
