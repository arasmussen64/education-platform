from checks import run


def test_python():
    """Typing python prints First: p, Last: n, Half: pyt."""
    printed = run("python\n")
    assert printed == "First: p\nLast: n\nHalf: pyt\n", f"Your program printed:\n{printed}"


def test_loops():
    """Typing loops prints First: l, Last: s, Half: lo."""
    printed = run("loops\n")
    assert printed == "First: l\nLast: s\nHalf: lo\n", f"Your program printed:\n{printed}"


def test_two_letters():
    """Typing hi prints First: h, Last: i, Half: h."""
    printed = run("hi\n")
    assert printed == "First: h\nLast: i\nHalf: h\n", f"Your program printed:\n{printed}"
