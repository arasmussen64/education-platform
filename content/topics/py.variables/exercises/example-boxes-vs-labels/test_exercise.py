from checks import run


def test_follows_the_names():
    """Prints Paris, then Tokyo, then Tokyo Lima."""
    assert run() == "Paris\nTokyo\nTokyo Lima\n"
