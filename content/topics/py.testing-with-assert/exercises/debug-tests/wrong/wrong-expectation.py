def average(a, b):
    """Return the average of two numbers."""
    return (a + b) / 2


def test_average():
    assert average(2, 4) == 3
    assert average(1, 2) == 1
    assert average(0, 0) == 0
    print("average: all checks passed")


if __name__ == "__main__":
    test_average()
