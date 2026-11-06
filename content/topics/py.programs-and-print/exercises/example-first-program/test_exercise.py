from checks import run


def test_prints_the_three_lines():
    """Prints the greeting, a blank line, and the sentence."""
    assert run() == "Hello, world!\n\nThis is my first program.\n"
