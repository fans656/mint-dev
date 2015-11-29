from pdu import *

class Frame(PDU):

    dst = Octet()
    src = Octet()
    payload = Bytes()
    checksum = Octet()

if __name__ == '__main__':
    frame = Frame('\xff')
