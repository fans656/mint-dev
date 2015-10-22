import sys

host = sys.argv[1]
port = int(sys.argv[2])
env = sys.argv[3]

def _ping():
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    s.send('hi')
    s.close()

execfile(env)
del sys, env
