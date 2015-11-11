#@after_worker_input
def _():
    title()
    put(a.nic._oframes)
    put(a.nic._oframe)
    a.port.show()
    l.ports[0].show()
    l.ports[1].show()
    b.port.show()
    put('isymbol: {}', b.nic.port.isymbol)
    put(b.nic._iframe)
    put(b.nic._iframes)
    raw_input()
