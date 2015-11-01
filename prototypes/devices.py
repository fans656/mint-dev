from mint.components import Endpoint
from mint.utils import format_bytes as fmt
from mint import utils
import mint

class PC(Endpoint):

    def __init__(self, name=None):
        super(PC, self).__init__(name)
        self.framer = Framer(self)

class Framer(object):
    '''
    send
        split data into several smaller part (called payload)
        add header and tail to each payload
        and escape the payload's content
        handover frame to lower layer
    recv
        detect frame's start and end
        unescape frame's payload
        handover to upper layer
    '''

    def __init__(self, endpoint):
        self.endpoint = endpoint
        self.port = self.endpoint.port
        self.group_size = 3
        self.flag = utils.unbitify('11111111')
        self.escape_byte = utils.unbitify('00000000')

    def send(self, data):
        payloads = self.split(data, self.group_size)
        for payload in payloads:
            payload = self.escape(payload, self.flag, self.escape_byte)
            frame = self.flag + payload + self.flag
            print 'frame sent by {}: {}'.format(self.endpoint, utils.format_bytes(frame))
            self.port.put(frame)

    @staticmethod
    def split(data, group_size):
        return utils.split_into(data, group_size)

    @staticmethod
    def escape(data, flag, escape_byte):
        ret = ''
        for byte in data:
            if byte == flag or byte == escape_byte:
                ret += escape_byte
            ret += byte
        return ret

    @staticmethod
    def unescape(data, escape_byte):
        ret = ''
        escaping = False
        for byte in data:
            if escaping:
                ret += byte
                escaping = False
            elif byte == escape_byte:
                escaping = True
            else:
                ret += byte
        return ret


    @mint.block
    def recv(self):
        data = ''
        flag = utils.bitify(self.flag)
        escape_byte = utils.bitify(self.escape_byte)
        # detect start flag
        while True:
            yield self.port.bit_arrive.event
            data += self.port.get(1)
            if data.endswith(flag):
                data = ''
                break
        # receive data until end flag
        while True:
            # receive 8 bits
            for _ in range(8):
                yield self.port.bit_arrive.event
                data += self.port.get(1)
            # check if is escaping
            if data.endswith(escape_byte):
                # delete the escaper byte
                data = data[:-8]
                # get the escapee byte
                for _ in range(8):
                    yield self.port.bit_arrive.event
                    data += self.port.get(1)
                continue
            # end flag detected
            if data.endswith(flag):
                data = data[:-8]
                break
        mint.ret(utils.unbitify(data))

if __name__ == '__main__':
    data = '\xff\x01\x00'
    print utils.format_bytes(data)
    edata = Framer.escape(data, '\xff', '\x00')
    print utils.format_bytes(edata, 'hex')
    print utils.format_bytes(Framer.unescape(edata, '\x00'), 'hex')
