from checks import run


def test_to_three():
    """Typing 3 prints 1, 2, 3."""
    printed = run("3\n")
    assert printed == "1\n2\n3\n", f"Your program printed:\n{printed}"


def test_to_one():
    """Typing 1 prints just 1."""
    printed = run("1\n")
    assert printed == "1\n", f"Your program printed:\n{printed}"


def test_to_zero():
    """Typing 0 prints nothing: the loop never runs."""
    printed = run("0\n")
    assert printed == "", f"Your program printed:\n{printed}"
