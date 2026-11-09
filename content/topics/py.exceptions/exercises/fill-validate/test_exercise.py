from checks import run


def test_bad_then_good():
    """Typing -2, abc, 5 prints both messages and then Twice that is 10."""
    got = run("-2\nabc\n5\n")
    assert got == "Must be more than 0.\nNot a whole number.\nTwice that is 10\n", (
        f"Your program printed:\n{got}"
    )


def test_good_first():
    """Typing 4 straight away prints Twice that is 8."""
    got = run("4\n")
    assert got == "Twice that is 8\n", f"Your program printed:\n{got}"
