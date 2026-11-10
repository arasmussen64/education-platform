from checks import run


def test_solves_and_checks():
    """Prints x = 6.0, then check: 11.0."""
    assert run() == "x = 6.0\ncheck: 11.0\n"
