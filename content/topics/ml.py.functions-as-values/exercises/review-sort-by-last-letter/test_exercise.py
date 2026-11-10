from checks import run, run_with


def test_these_words():
    """Prints ['banana', 'fig', 'cherry']: a, g, y."""
    assert run() == "['banana', 'fig', 'cherry']\n"


def test_other_words():
    """Sorts by last letter, not first: ['axe', 'bob', 'cat'] gives bob, axe, cat."""
    assert run_with({"words": ["axe", "bob", "cat"]}) == "['bob', 'axe', 'cat']\n"
