from checks import run


def test_adds_the_numbers():
    """Line 1 is 10 plus 5, added as numbers."""
    printed = run()
    assert printed.splitlines()[:1] == ["15"], (
        f"Line 1 should be 15. Your program printed:\n{printed}"
    )


def test_joins_the_text():
    """Line 2 is the text "10" joined to "5"."""
    printed = run()
    assert printed.splitlines()[1:2] == ["105"], (
        f"Line 2 should be 105. Your program printed:\n{printed}"
    )


def test_shows_the_type():
    """Line 3 shows the type of 10.5, and nothing comes after it."""
    printed = run()
    assert printed.splitlines()[2:] == ["<class 'float'>"], (
        f"Line 3 should be <class 'float'>, and the last line. "
        f"Your program printed:\n{printed}"
    )
