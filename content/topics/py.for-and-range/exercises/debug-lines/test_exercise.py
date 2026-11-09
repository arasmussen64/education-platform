from checks import run


def expected(n):
    lines = "".join(f"Line {i}\n" for i in range(1, n + 1))
    return f"{lines}Ready\nReady\nReady\nLines printed: {n}\n"


def test_two():
    """Typing 2 prints Line 1, Line 2, Ready three times, then Lines printed: 2."""
    printed = run("2\n")
    assert printed == expected(2), f"Your program printed:\n{printed}"


def test_four():
    """Typing 4 prints four numbered lines and ends with Lines printed: 4."""
    printed = run("4\n")
    assert printed == expected(4), f"Your program printed:\n{printed}"
