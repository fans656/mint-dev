from bitarray import bitarray

DELIMITER = bitarray('01111110', endian='big')

def bits(bytes):
    r = bitarray(endian='big')
    r.frombytes(bytes)
    return r

def stuffed(data):
    ret = bitarray(DELIMITER, endian='big')
    count = 0
    for bit in bits(data):
        ret.append(bit)
        if bit:
            count += 1
            if count == 5:
                ret.append(0)
                count = 0
        else:
            count = 0
    return ret + DELIMITER

if __name__ == '__main__':
    print stuffed('\x01\x02\xff')
