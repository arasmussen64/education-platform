from checks import run


def test_asks_again():
    """Typing abc, then 30, prints the message and then the age next year."""
    assert run("abc\n30\n") == "That's not a whole number. Try again.\nNext year you'll be 31.\n"


def test_first_time_right():
    """Typing 7 straight away prints just the result."""
    assert run("7\n") == "Next year you'll be 8.\n"
