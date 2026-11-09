def absolute(n):
    """Return n without its sign."""
    if n < 0:
        return -n
    return n


def test_absolute():
    assert absolute(-5) == 5
    assert absolute(3) == 3
    assert absolute(0) == 0
    print("absolute: all checks passed")


if __name__ == "__main__":
    test_absolute()
