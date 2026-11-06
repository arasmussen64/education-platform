from checks import run


def test_prints_the_four_types():
    """Prints the type of each of the four values."""
    expected = ["<class 'str'>", "<class 'int'>", "<class 'float'>", "<class 'str'>"]
    assert run().splitlines() == expected
