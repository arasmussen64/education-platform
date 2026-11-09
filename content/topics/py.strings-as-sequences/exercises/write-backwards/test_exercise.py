from checks import run


def test_stressed():
    """Typing stressed prints desserts."""
    printed = run("stressed\n")
    assert printed == "desserts\n", f"Your program printed:\n{printed}"


def test_short_words():
    """Typing ab prints ba, and a single letter prints itself."""
    printed = run("ab\n")
    assert printed == "ba\n", f"Typing ab: your program printed:\n{printed}"
    printed = run("x\n")
    assert printed == "x\n", f"Typing x: your program printed:\n{printed}"
