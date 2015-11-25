class NIC(object):

    def __init__(self, device):
        self.device = device

    def send(self, data):
        peer = self.device.get_peer()
        peer.send(data)

    def recv(self, nbits=16):
        peer = self.device.get_peer()
        peer.recv(data)
