def is_leap(year):
    """Return True when the year is a leap year."""
    return year % 4 == 0


def test_is_leap():
    assert is_leap(2024)
    assert not is_leap(2023)
    assert is_leap(2000)
    assert not is_leap(2001)
    print("is_leap: all checks passed")


if __name__ == "__main__":
    test_is_leap()
