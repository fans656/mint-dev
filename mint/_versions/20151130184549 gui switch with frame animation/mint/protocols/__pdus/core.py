from pdu import *

class Packet(PDU):

    src = DWord()
    dst = DWord()
    payload = Octets()

class Frame(PDU):

    dst = Octet()
    src = Octet()
    payload = Packet()
    checksum = Octet()

if __name__ == '__main__':
    #frame = Frame('\xff')
    print Packet()
