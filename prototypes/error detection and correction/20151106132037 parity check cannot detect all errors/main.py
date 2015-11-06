import operator
from protocol import Protocol
from parity import EvenParityProtocol, OddParityProtocol
import error
from utils import occurrence_rate

bits = '0' * 8
bit_flip_rate = 0.01

n_bytes = int(1e4)
n_detected = 0
n_errors = 0

for _ in range(n_bytes):
    try:
        EvenParityProtocol(bits, error.random_flip(bit_flip_rate))
    except Protocol.FalseTransmission as e:
        if isinstance(e, Protocol.ErrorDetected):
            n_detected += 1
        n_errors += 1

print '{:.2f}% errors({}/{}) detected in {} bytes trasmission'.format(
        n_detected * 100.0 / n_errors, n_detected, n_errors, n_bytes)
