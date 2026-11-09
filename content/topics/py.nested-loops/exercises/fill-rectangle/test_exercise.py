from checks import run


def test_four_by_two():
    """Typing 4 and 2 prints two rows of four stars."""
    printed = run("4\n2\n")
    assert printed == "****\n****\n", f"Your program printed:\n{printed}"


def test_one_by_three():
    """Typing 1 and 3 prints three rows of one star."""
    printed = run("1\n3\n")
    assert printed == "*\n*\n*\n", f"Your program printed:\n{printed}"


def test_three_by_one():
    """Typing 3 and 1 prints one row of three stars."""
    printed = run("3\n1\n")
    assert printed == "***\n", f"Your program printed:\n{printed}"
