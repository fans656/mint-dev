'''
Keep wondering why with parity check the false trasmission rate is higher.
Then I realize that parity check will append 1 more bit to the origial data,
this will increese the byte fallacy probability!

E.g. for bit flip rate R,
with 8 bits, the byte fallacy rate R_8 = 1 - (1 - R) ^ 8
parity check add one parity bit to the byte, end up with a 9 bits sequence and
with 9 bits, the byte fallacy rate R_9 = 1 - (1 - R) ^ 9
    (1 - R) ^ 9 < (1- R) ^ 8
thus R_9 > R_8
'''
import operator
from protocol import Protocol
from parity import EvenParityProtocol, OddParityProtocol
import error
from utils import occurrence_rate

def byte_wrong():
    try:
        EvenParityProtocol(bits, error.random_flip(bit_flip_rate))
    except Protocol.FalseTransmission:
        return True

def byte_wrong_():
    return bits != error.random_flip(bit_flip_rate)(bits)

bits = '0' * 8
bit_flip_rate = 0.01
byte_wrong_rate = 1 - (1 - bit_flip_rate) ** 8
n_executions = 1e4

print 'Theoretical rate:     {}'.format(byte_wrong_rate)
print 'With parity check:    {}'.format(occurrence_rate(byte_wrong, int(n_executions)))
print 'Without parity check: {}'.format(occurrence_rate(byte_wrong_, int(n_executions)))
