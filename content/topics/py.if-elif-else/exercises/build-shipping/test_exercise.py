from checks import run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).


def test_light():
    """A 0.5 kg parcel costs $5.00."""
    assert run("0.5\n") == "Shipping: $5.00\n"


def test_medium():
    """A 3 kg parcel costs $9.50."""
    assert run("3\n") == "Shipping: $9.50\n"


def test_heavy():
    """A 12 kg parcel costs $20.00."""
    assert run("12\n") == "Shipping: $20.00\n"


def test_boundaries():
    """Exactly 1 kg still costs $5.00, and exactly 5 kg still costs $9.50."""
    assert run("1\n") == "Shipping: $5.00\n"
    assert run("5\n") == "Shipping: $9.50\n"


def test_decimals():
    """Weights with decimals work: 1.2 kg costs $9.50."""
    assert run("1.2\n") == "Shipping: $9.50\n"
