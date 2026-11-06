from checks import run


def test_greets_and_counts():
    """Greets Ada, and says she'll be 37 next year."""
    assert run("Ada\n36\n") == "Hello, Ada!\nNext year you'll be 37.\n"
