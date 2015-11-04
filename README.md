# mint

A Python library for computer network simulation.

Example usage:

    from mint import *
    
    h1 = Host()
    h2 = Host()
    hub = Hub()
    link(h1, hub.ports[0])
    link(hub.ports[1], h2)
    
    @proc
    def _():
        h1.port.send('111')
    
    @proc
    def _():
        print h2.port.recv(8)
    
    run()

Output:
    
    00011100
