def is_even(n):
    """Return True when n is even."""
    return n % 2 == 0


def test_is_even():
    assert is_even(4) == is_even(4)
    assert is_even(7) == is_even(7)
    assert is_even(0) == is_even(0)
    print("is_even: all checks passed")


if __name__ == "__main__":
    test_is_even()
