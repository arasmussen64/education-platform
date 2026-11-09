from checks import run


def test_three():
    """Typing 3, then 4, 5, 9, prints Average: 6.0."""
    printed = run("3\n4\n5\n9\n")
    assert printed == "Average: 6.0\n", f"Your program printed:\n{printed}"


def test_two():
    """Typing 2, then 3, 4, prints Average: 3.5: the decimals are kept."""
    printed = run("2\n3\n4\n")
    assert printed == "Average: 3.5\n", f"Your program printed:\n{printed}"


def test_one():
    """Typing 1, then 7, prints Average: 7.0."""
    printed = run("1\n7\n")
    assert printed == "Average: 7.0\n", f"Your program printed:\n{printed}"
