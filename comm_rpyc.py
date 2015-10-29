import rpyc
from communication import Thread, host, port

def run(self):
    from rpyc.utils.server import ThreadedServer
    ThreadedServer(rpyc.SlaveService, hostname=host, port=port).start()

Thread.run = run
