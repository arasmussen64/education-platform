from checks import run


def test_next_year():
    """Typing Ada and 36 prints Ada will be 37 next year."""
    assert run("Ada\n36\n") == "Ada will be 37 next year.\n"
