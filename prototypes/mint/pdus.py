import struct

class Frame(object):

    def __init__(self, raw):
        self.raw = raw
        (self.dst,
         self.src) = struct.unpack('!BB', raw[:2])
        self.payload = raw[2:]

    def __repr__(self):
        return '<Frame src:{}, dst:{}, with payload of length {}>'.format(
            self.src, self.dst, len(self.payload)
        )

if __name__ == '__main__':
    frame = Frame('\x01\x02\xffhello world')
    print frame
