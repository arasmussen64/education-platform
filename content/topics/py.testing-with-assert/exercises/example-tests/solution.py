def square(n):
    """Return n times n."""
    return n * n


def test_square():
    assert square(2) == 4
    assert square(3) == 9
    assert square(-2) == 4
    assert square(0) == 0
    print("square: all checks passed")


if __name__ == "__main__":
    test_square()
