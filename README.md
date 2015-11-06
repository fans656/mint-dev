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

Up to application layer, write application just as application:

    # server.py
    from mint import socket
    
    listen_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listen_sock.bind(8080)
    listen_sock.listen()
    while True:
        sock, addr = listen_sock.accept()
        print 'Connection established with', addr
        msg = ''
        while True:
            ch = sock.recv(1)
            msg += ch
            if ch == '\n':
                break
        sock.send('You said: ' + msg)
        sock.close()
    
    # client.py
    from mint import socket

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect('192.168.0.2')
    sock.send('hello server\n')
    msg = ''
    while True:
        ch = sock.recv(1)
        msg += ch
        if ch == '\n':
            break
    print msg

Down to physical layer, model the link channal behaviour as you wish:
    
    # main.py
    from mint import *
    
    a = Host(ip='192.168.0.2', script='server.py')
    b = Host(ip='192.168.0.3', script='client.py', wait=1)
    switch = Switch()

    link(a, switch.ports[0])
    link(b, switch.ports[1], latency=20, error_func=error.flip_bit(ith=3))
    
    run()
