from checks import run


def test_child_on_a_saturday():
    """Typing 10, Sat and no prints Ticket: child and Price: $8.00."""
    printed = run("10\nSat\nno\n")
    assert printed == "Ticket: child\nPrice: $8.00\n", f"Your program printed:\n{printed}"


def test_every_band():
    """3 is free, 12 a child, 13 an adult, 65 a senior, all on a Monday without membership."""
    for age, expected in [
        (3, "Ticket: free\nPrice: $0.00\n"),
        (12, "Ticket: child\nPrice: $6.00\n"),
        (13, "Ticket: adult\nPrice: $12.00\n"),
        (65, "Ticket: senior\nPrice: $8.00\n"),
    ]:
        printed = run(f"{age}\nMon\nno\n")
        assert printed == expected, (
            f"Typing {age}, Mon and no should print:\n{expected}Your program printed:\n{printed}"
        )
