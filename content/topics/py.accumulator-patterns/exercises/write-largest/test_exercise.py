from checks import run


def test_three():
    """Typing 3, then 4, 9, 2, prints 9."""
    printed = run("3\n4\n9\n2\n")
    assert printed == "9\n", f"Your program printed:\n{printed}"


def test_one():
    """Typing 1, then 5, prints 5."""
    printed = run("1\n5\n")
    assert printed == "5\n", f"Your program printed:\n{printed}"


def test_largest_first():
    """Typing 4, then 7, 7, 3, 1, prints 7: the largest isn't always the last."""
    printed = run("4\n7\n7\n3\n1\n")
    assert printed == "7\n", f"Your program printed:\n{printed}"
