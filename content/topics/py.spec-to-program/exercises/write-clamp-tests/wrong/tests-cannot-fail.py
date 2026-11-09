def test_clamp():
    assert clamp(5, 0, 10) == 5
    assert clamp(3, 0, 10) == 3
    assert clamp(7, 0, 10) == 7
    assert clamp(0, 0, 10) == 0
    print("clamp: all checks passed")


def clamp(n, low, high):
    """Return n, held between low and high."""
    if n < low:
        return low
    if n > high:
        return high
    return n
