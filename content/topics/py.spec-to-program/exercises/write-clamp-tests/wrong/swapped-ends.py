def test_clamp():
    assert clamp(5, 0, 10) == 5
    assert clamp(-3, 0, 10) == 0
    assert clamp(42, 0, 10) == 10
    assert clamp(10, 0, 10) == 10
    print("clamp: all checks passed")


def clamp(n, low, high):
    """Return n, held between low and high."""
    if n < low:
        return high
    if n > high:
        return low
    return n
