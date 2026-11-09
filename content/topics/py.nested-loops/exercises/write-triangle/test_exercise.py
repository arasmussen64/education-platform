from checks import run


def test_three():
    """Typing 3 prints rows of 1, 2 and 3 stars."""
    printed = run("3\n")
    assert printed == "*\n**\n***\n", f"Your program printed:\n{printed}"


def test_one():
    """Typing 1 prints a single star."""
    printed = run("1\n")
    assert printed == "*\n", f"Your program printed:\n{printed}"


def test_four():
    """Typing 4 prints four rows, the last with four stars."""
    printed = run("4\n")
    assert printed == "*\n**\n***\n****\n", f"Your program printed:\n{printed}"
