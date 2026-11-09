from checks import run


def test_education():
    """Typing education prints 5."""
    printed = run("education\n")
    assert printed == "5\n", f"Your program printed:\n{printed}"


def test_rhythm():
    """Typing rhythm prints 0."""
    printed = run("rhythm\n")
    assert printed == "0\n", f"Your program printed:\n{printed}"


def test_queue():
    """Typing queue prints 4: every vowel counts, including repeats."""
    printed = run("queue\n")
    assert printed == "4\n", f"Your program printed:\n{printed}"
