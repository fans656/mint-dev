import mint
from mint.utils import mac_from_bytes
from mint.protocols.pdus import Frame, MAC

class Framer(object):

    def __init__(self, delimiter, mac, handlers=None):
        if handlers is None:
            handlers = {}
        self.handlers = handlers
        self.delimiter = delimiter
        self.mac = mac
        mint.worker(self.run)

    def send(self, data, to, ethertype=Frame.EtherType.IPv4):
        frame = Frame(
            dst=to,
            src=self.mac,
            ethertype=ethertype,
            payload=data,
        )
        self.delimiter.send(frame.raw)

    def run(self):
        while True:
            raw = self.delimiter.recv()
            frame = Frame(raw)
            if self.for_me(frame.dst):
                try:
                    handler = self.handlers[frame.ethertype]
                except KeyError:
                    mint.report('no handler for {}'.format(
                        Frame.EtherType[frame.ethertype]
                    ))
                else:
                    handler(frame.payload)
            else:
                msg = '{:02x} dropped frame from {:02x} to {:02x}: {}'
                mint.report(msg.format(
                    mac_from_bytes(self.mac),
                    mac_from_bytes(frame.src),
                    mac_from_bytes(frame.dst),
                    repr(frame.payload)
                ))

    def for_me(self, mac):
        return mac == MAC.Broadcast or mac == self.mac
