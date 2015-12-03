import sys
import rpyc
import os

host = sys.argv[1]
port = int(sys.argv[2])
env = sys.argv[3]

c = rpyc.classic.connect(host, port=port)
o = c.modules.communication.console_object
execfile(os.path.join(o.device.path, 'console.py'))
