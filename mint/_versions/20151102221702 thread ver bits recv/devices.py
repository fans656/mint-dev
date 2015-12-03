from mint.components import Endpoint
from mint.utils import format_bytes as fmt
from mint import utils
import mint

class PC(Endpoint):

    def __init__(self, name=None):
        super(PC, self).__init__(name)

    def send(self, data):
        self.port.send(data)

    def recv(self, nbits):
        data = ''
        for _ in range(nbits):
            data += self.port.recv(1)
        return data
