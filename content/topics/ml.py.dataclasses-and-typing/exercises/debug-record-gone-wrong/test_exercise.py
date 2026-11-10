from checks import function, run

EXPECTED = "Ticket(event='Concert', price=45.0, row='B')\n90.0\n"


def test_the_output():
    """Prints the ticket, then 90.0."""
    printed = run()
    assert printed == EXPECTED, f"Expected this:\n{EXPECTED}\nYour program printed:\n{printed}"


def test_the_record():
    """Ticket is a dataclass whose default price is the number 45.0."""
    Ticket = function("Ticket")
    assert Ticket.__dataclass_fields__.keys() == {"event", "price", "row"}
    assert Ticket("Play").price == 45.0
    assert Ticket("Play", 10.0, "A") == Ticket("Play", 10.0, "A")
