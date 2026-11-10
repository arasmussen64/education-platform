from checks import function, run


def test_the_output():
    """Prints 37 255 1 128."""
    printed = run()
    assert printed == '37 255 1 128\n', f"Your program printed:\n{printed}"


def test_against_int():
    """Agrees with int(bits, 2) for every value from 0 to 1023, written in 10 bits."""
    from_bits = function("from_bits")
    assert all(from_bits(format(n, "010b")) == n for n in range(1024))
