from checks import run


def test_minutes_and_seconds():
    """Prints 2.25, then 2 minutes and 15 seconds."""
    assert run() == "2.25\n2 minutes and 15 seconds\n"
