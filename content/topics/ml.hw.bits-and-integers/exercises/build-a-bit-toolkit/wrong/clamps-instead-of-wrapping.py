import numpy as np

DIGITS = "0123456789abcdef"


def to_base(n, base):
    """A non-negative integer as a string of digits in a base from 2 to 16."""
    if n == 0:
        return "0"
    digits = []
    while n > 0:
        digits.append(DIGITS[n % base])
        n //= base
    return "".join(reversed(digits))


def wraps_to(value, bits, signed):
    """The value a fixed-width integer of that many bits holds after storing value: it wraps around."""
    low, high = (-(2 ** (bits - 1)), 2 ** (bits - 1) - 1) if signed else (0, 2 ** bits - 1)
    return max(low, min(high, value))


def array_bytes(shape, dtype):
    """How many bytes an array of that shape and dtype takes."""
    count = 1
    for size in shape:
        count *= size
    return count * np.dtype(dtype).itemsize


def smallest_uint(max_value):
    """The smallest unsigned dtype name that holds counts from 0 to max_value."""
    for name in ("uint8", "uint16", "uint32", "uint64"):
        if max_value <= np.iinfo(name).max:
            return name
    raise ValueError("too large for 64 bits")


print(to_base(37, 2), to_base(255, 16), to_base(255, 2), to_base(0, 2))
print(wraps_to(128, 8, True), wraps_to(256, 8, False), wraps_to(-1, 8, False), wraps_to(127, 8, True))
print(array_bytes((1000, 784), "float32"), array_bytes((1000, 784), "uint8"), array_bytes((60000, 28, 28), "float64"))
print(smallest_uint(200), smallest_uint(60000), smallest_uint(3_000_000_000))
