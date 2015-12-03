class Frame(object):

    def __init__(self, data):
        self.src_addr = 0
        self.dst_addr = 1
        self.data = data

    def __str__(self):
        return self.data
