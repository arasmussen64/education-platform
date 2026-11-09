from checks import run


def test_three():
    """Typing 3 prints 1, 4, 9."""
    printed = run("3\n")
    assert printed == "1\n4\n9\n", f"Your program printed:\n{printed}"


def test_one_and_five():
    """Typing 1 prints just 1; typing 5 prints 1, 4, 9, 16, 25."""
    printed = run("1\n")
    assert printed == "1\n", f"Typing 1: your program printed:\n{printed}"
    printed = run("5\n")
    assert printed == "1\n4\n9\n16\n25\n", f"Typing 5: your program printed:\n{printed}"
