from checks import run


def test_estimates_settle():
    """Prints 6.1, then 6.001."""
    assert run() == "6.1\n6.001\n"
