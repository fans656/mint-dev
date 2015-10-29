import sys
import rpyc

host = sys.argv[1]
port = int(sys.argv[2])
env = sys.argv[3]

c = rpyc.classic.connect(host, port=port)
o = c.modules.communication.console_object
