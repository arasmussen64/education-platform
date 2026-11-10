import math
import struct

import numpy as np


def decode_float32(x):
    """(sign bit, unbiased exponent, mantissa bits) of x stored as a float32."""
    bits = struct.unpack(">I", struct.pack(">f", x))[0]
    return bits >> 31, ((bits >> 23) & 0xFF) - 127, bits & 0x7FFFFF


def close(a, b, rel=1e-9, abs_=0.0):
    """Whether a and b agree within a relative tolerance of the larger, or an absolute one."""
    return abs(a - b) <= max(rel * max(abs(a), abs(b)), abs_)


def kahan_sum(values):
    """A float32 sum that carries its rounding error forward."""
    total = np.float32(0)
    carry = np.float32(0)
    for value in values:
        adjusted = np.float32(value) - carry
        new_total = total + adjusted
        carry = (new_total - total) - adjusted
        total = new_total
    return float(total)


def log_sum_exp(xs):
    """log(sum(exp(xs))) without overflowing: pull the largest term out first."""
    biggest = max(xs)
    return biggest + math.log(sum(math.exp(x - biggest) for x in xs))


def softmax(xs):
    """exp(xs) scaled to sum to 1, computed the stable way."""
    biggest = max(xs)
    weights = [math.exp(x - biggest) for x in xs]
    total = sum(weights)
    return [w / total for w in weights]


print(decode_float32(1.0), decode_float32(-2.5), decode_float32(0.1))
print(close(0.1 + 0.2, 0.3), close(1.0, 1.0 + 1e-6), close(0.0, 1e-12, abs_=1e-9))
print(round(kahan_sum([0.1] * 100_000), 3))
print(round(log_sum_exp([1000.0, 1001.0]), 6), [round(p, 6) for p in softmax([1000.0, 1001.0])])
