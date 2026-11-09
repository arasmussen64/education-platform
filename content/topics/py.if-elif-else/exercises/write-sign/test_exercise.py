from checks import run


def test_positive():
    """Typing 5 prints Positive."""
    printed = run("5\n")
    assert printed == "Positive\n", f"Your program printed:\n{printed}"


def test_negative():
    """Typing -3 prints Negative."""
    printed = run("-3\n")
    assert printed == "Negative\n", f"Your program printed:\n{printed}"


def test_zero():
    """Typing 0 prints Zero: it's neither positive nor negative."""
    printed = run("0\n")
    assert printed == "Zero\n", f"Your program printed:\n{printed}"
