from checks import run


def test_more_apples():
    """Typing 5 and 3 prints More apples, by 2."""
    printed = run("5\n3\n")
    assert printed == "More apples, by 2\n", f"Your program printed:\n{printed}"


def test_more_oranges():
    """Typing 2 and 6 prints More oranges, by 4."""
    printed = run("2\n6\n")
    assert printed == "More oranges, by 4\n", f"Your program printed:\n{printed}"


def test_same():
    """Typing 4 and 4 prints Same number."""
    printed = run("4\n4\n")
    assert printed == "Same number\n", f"Your program printed:\n{printed}"
