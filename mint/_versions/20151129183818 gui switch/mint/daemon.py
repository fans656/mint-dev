import rpyc

def start(port=6560):
    from rpyc.utils.server import ThreadedServer as Server
    Server(rpyc.SlaveService, port=port).start()
