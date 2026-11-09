import math


def shipping(weight):
    """Return the cost of shipping a parcel of this weight in kg."""
    if weight <= 1:
        return 5.0
    extra_kg = math.ceil(weight - 1)
    return 5.0 + 1.0 * extra_kg


def test_shipping():
    assert shipping(0.5) == 5.0
    assert shipping(1) == 5.0
    assert shipping(1.2) == 6.0
    assert shipping(3) == 7.0
    print("shipping: all checks passed")


def main():
    """Price one parcel."""
    print(f"2.5 kg: {shipping(2.5):.2f}")


if __name__ == "__main__":
    test_shipping()
    main()
