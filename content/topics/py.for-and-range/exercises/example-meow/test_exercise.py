from checks import run


def test_prints_both_loops():
    """Prints 0 hello, 1 hello, 2 hello, meow, meow, done."""
    assert run() == "0 hello\n1 hello\n2 hello\nmeow\nmeow\ndone\n"
