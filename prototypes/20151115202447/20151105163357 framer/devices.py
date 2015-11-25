import mint
from framer import BitStuffingFramer

class PC(mint.Host):

    def __init__(self, name=None):
        super(PC, self).__init__(name)
        self.framer = BitStuffingFramer(self.port)

    def send(self, data):
        data = mint.utils.bitify(data)
        self.framer.send(data)

    def recv(self, nbytes):
        nbits = nbytes * 8
        data = ''
        while len(data) < nbits:
            recved = self.framer.recv()
            data += recved
        return mint.utils.unbitify(data)

if __name__ == '__main__':
    pass
