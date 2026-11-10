from checks import run, run_with


def test_these_words():
    """Prints ['MOON', 'STAR', 'PLANET']."""
    printed = run()
    assert printed == "['MOON', 'STAR', 'PLANET']\n", f"Your program printed:\n{printed}"


def test_other_words():
    """Works for other words: only 'bbbb' survives from ['a', 'bbbb', 'cc']."""
    printed = run_with({"words": ["a", "bbbb", "cc"]})
    assert printed == "['BBBB']\n", f"With ['a', 'bbbb', 'cc'] it should print ['BBBB']. It printed:\n{printed}"
