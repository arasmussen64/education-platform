from checks import run


def test_eighteen():
    """Typing 18 prints Adult: True, Exactly 18: True, Under 13: False."""
    printed = run("18\n")
    expected = "Adult: True\nExactly 18: True\nUnder 13: False\n"
    assert printed == expected, f"Your program printed:\n{printed}"


def test_twelve():
    """Typing 12 prints Adult: False, Exactly 18: False, Under 13: True."""
    printed = run("12\n")
    expected = "Adult: False\nExactly 18: False\nUnder 13: True\n"
    assert printed == expected, f"Your program printed:\n{printed}"


def test_thirteen():
    """Typing 13 prints Under 13: False, because 13 is not under 13."""
    printed = run("13\n")
    expected = "Adult: False\nExactly 18: False\nUnder 13: False\n"
    assert printed == expected, f"Your program printed:\n{printed}"


def test_thirty():
    """Typing 30 prints Adult: True, Exactly 18: False, Under 13: False."""
    printed = run("30\n")
    expected = "Adult: True\nExactly 18: False\nUnder 13: False\n"
    assert printed == expected, f"Your program printed:\n{printed}"
