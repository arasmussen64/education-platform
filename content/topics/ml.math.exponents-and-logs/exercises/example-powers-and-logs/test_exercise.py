from checks import run


def test_powers_and_logs():
    """Prints 1024, 0.25, 4.0, 10.0 and 2.0."""
    assert run() == "1024\n0.25\n4.0\n10.0\n2.0\n"
