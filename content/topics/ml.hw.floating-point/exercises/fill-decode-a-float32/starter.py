import struct


def decode_float32(x):
    """The sign bit, the stored exponent and the mantissa bits of x as a float32."""
    bits = struct.unpack(">I", struct.pack(">f", x))[0]
    sign = bits >> 31
    exponent = (bits >> ...) & 0xFF
    mantissa = bits & ...
    return sign, exponent, mantissa


for x in (1.0, -2.5, 0.1):
    sign, exponent, mantissa = decode_float32(x)
    value = (-1) ** sign * (1 + mantissa / 2**23) * 2 ** (exponent - 127)
    print(x, "->", sign, exponent - 127, mantissa, "->", value)
