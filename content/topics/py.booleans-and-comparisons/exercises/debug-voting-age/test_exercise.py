from checks import run


def test_eighteen():
    """Typing 18 prints Old enough: True, Exactly the limit: True, Teen or older: True."""
    printed = run("18\n")
    expected = "Old enough: True\nExactly the limit: True\nTeen or older: True\n"
    assert printed == expected, f"Your program printed:\n{printed}"


def test_thirteen():
    """Typing 13 prints Old enough: False, Exactly the limit: False, Teen or older: True."""
    printed = run("13\n")
    expected = "Old enough: False\nExactly the limit: False\nTeen or older: True\n"
    assert printed == expected, f"Your program printed:\n{printed}"


def test_twelve():
    """Typing 12 prints False, False, False."""
    printed = run("12\n")
    expected = "Old enough: False\nExactly the limit: False\nTeen or older: False\n"
    assert printed == expected, f"Your program printed:\n{printed}"
