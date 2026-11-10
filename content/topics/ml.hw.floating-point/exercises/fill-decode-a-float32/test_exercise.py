from checks import function, run


def test_the_output():
    """Prints the three decoded values."""
    printed = run()
    assert printed == '1.0 -> 0 0 0 -> 1.0\n-2.5 -> 1 1 2097152 -> -2.5\n0.1 -> 0 -4 5033165 -> 0.10000000149011612\n', f"Your program printed:\n{printed}"


def test_more_values():
    """2.0 is exponent 128 with a zero mantissa; 0.5 is exponent 126; the parts rebuild 3.75 exactly."""
    decode_float32 = function("decode_float32")
    assert decode_float32(2.0) == (0, 128, 0) and decode_float32(0.5) == (0, 126, 0)
    sign, exponent, mantissa = decode_float32(3.75)
    assert (-1) ** sign * (1 + mantissa / 2**23) * 2 ** (exponent - 127) == 3.75
