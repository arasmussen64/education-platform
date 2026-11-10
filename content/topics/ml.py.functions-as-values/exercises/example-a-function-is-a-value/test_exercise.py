from checks import run


def test_the_walkthrough():
    """Prints HELLO!, hello..., the words by length, the numbers by size, then [1, 3]."""
    assert run() == "HELLO!\nhello...\n['fig', 'pear', 'banana']\n[3, 5, -7]\n[1, 3]\n"
