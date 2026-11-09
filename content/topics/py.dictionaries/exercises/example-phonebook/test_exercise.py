from checks import run


def test_phone_book():
    """Prints Ada's number, the count, False for Dee, then every entry."""
    assert run() == "555-1234\n3\nFalse\nAda 555-1234\nBob 555-1111\nCy 555-0000\n"
