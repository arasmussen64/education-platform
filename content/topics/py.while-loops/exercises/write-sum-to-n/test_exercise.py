from checks import run


def test_four():
    """Typing 4 prints 10."""
    printed = run("4\n")
    assert printed == "10\n", f"Your program printed:\n{printed}"


def test_one_and_ten():
    """Typing 1 prints 1, and typing 10 prints 55."""
    printed = run("1\n")
    assert printed == "1\n", f"Typing 1: your program printed:\n{printed}"
    printed = run("10\n")
    assert printed == "55\n", f"Typing 10: your program printed:\n{printed}"
