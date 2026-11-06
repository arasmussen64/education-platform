from checks import run


def test_three_by_four():
    """Typing 3 and 4 prints Area: 12."""
    printed = run("3\n4\n")
    assert printed == "Area: 12\n", f"Your program printed:\n{printed}"


def test_ten_by_five():
    """Typing 10 and 5 prints Area: 50."""
    printed = run("10\n5\n")
    assert printed == "Area: 50\n", f"Your program printed:\n{printed}"
