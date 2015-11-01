class Line(object):

    def __init__(self, device):
        self.device = device

    def send(self, data):
        self.device.get_peer().send(data)

    def recv(self):
        return self.device.get_peer().recv()
