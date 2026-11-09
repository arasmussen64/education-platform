def to_fahrenheit(celsius):
    """Return the temperature in Fahrenheit."""
    return celsius * 9 / 5 + 32


def test_to_fahrenheit():
    assert to_fahrenheit(0) == 32
    assert to_fahrenheit(100) == 200
    assert to_fahrenheit(-40) == -40
    print("to_fahrenheit: all checks passed")


if __name__ == "__main__":
    test_to_fahrenheit()
