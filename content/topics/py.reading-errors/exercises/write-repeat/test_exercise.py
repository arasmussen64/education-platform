from checks import run


def test_hi_three_times():
    """Typing hi and 3 prints hihihi."""
    printed = run("hi\n3\n")
    assert printed == "hihihi\n", f"Your program printed:\n{printed}"


def test_other_words():
    """Typing ab and 2 prints abab; typing yes and 1 prints yes."""
    printed = run("ab\n2\n")
    assert printed == "abab\n", f"Your program printed:\n{printed}"
    printed = run("yes\n1\n")
    assert printed == "yes\n", f"Your program printed:\n{printed}"
