import mint
from framer import BitStuffingFramer

class PC(mint.Host):

    def __init__(self, name=None):
        super(PC, self).__init__(name)
        self.framer = BitStuffingFramer(self.port)
        self.data = ''

    def send(self, data):
        self.framer.send(data)

    def recv(self, nbytes):
        while len(self.data) < nbytes:
            self.data += self.framer.recv()
        ret, self.data = mint.utils.split_at(self.data, nbytes)
        return ret

if __name__ == '__main__':
    pass
