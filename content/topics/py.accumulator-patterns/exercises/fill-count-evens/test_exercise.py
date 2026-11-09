from checks import run


def test_ten():
    """Typing 10 prints 5: the evens are 2, 4, 6, 8 and 10."""
    printed = run("10\n")
    assert printed == "5\n", f"Your program printed:\n{printed}"


def test_seven():
    """Typing 7 prints 3."""
    printed = run("7\n")
    assert printed == "3\n", f"Your program printed:\n{printed}"


def test_one():
    """Typing 1 prints 0: there are no even numbers from 1 to 1."""
    printed = run("1\n")
    assert printed == "0\n", f"Your program printed:\n{printed}"
