from checks import run


def test_child():
    """Typing 8 prints Ticket: $6, then Enjoy the show!"""
    assert run("8\n") == "Ticket: $6\nEnjoy the show!\n"


def test_adult():
    """Typing 30 prints Ticket: $10, then Enjoy the show!"""
    assert run("30\n") == "Ticket: $10\nEnjoy the show!\n"
