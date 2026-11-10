def from_bits(bits):
    """The value of a string of bits, most significant first: each step doubles what came before and adds the next bit."""
    value = 0
    for bit in bits:
        value = value * ... + int(...)
    return value


print(from_bits("00100101"), from_bits("11111111"), from_bits("1"), from_bits("10000000"))
