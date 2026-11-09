from checks import run


def test_three_and_five():
    """Typing 3 and 5 prints Equal: False, First is smaller: True, Different: True."""
    assert run("3\n5\n") == "Equal: False\nFirst is smaller: True\nDifferent: True\n"


def test_four_and_four():
    """Typing 4 and 4 prints Equal: True, First is smaller: False, Different: False."""
    assert run("4\n4\n") == "Equal: True\nFirst is smaller: False\nDifferent: False\n"
