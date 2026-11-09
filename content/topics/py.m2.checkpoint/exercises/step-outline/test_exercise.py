from checks import run


def test_child_on_a_saturday():
    """Typing 10, Sat and no prints Ticket: child and Price: $8.00."""
    printed = run("10\nSat\nno\n")
    assert printed == "Ticket: child\nPrice: $8.00\n", f"Your program printed:\n{printed}"


def test_other_tickets():
    """An adult member on a Saturday pays $12.60, a senior on a Monday $8.00, a toddler nothing."""
    for typed, expected in [
        ("30\nSat\nyes\n", "Ticket: adult\nPrice: $12.60\n"),
        ("70\nMon\nno\n", "Ticket: senior\nPrice: $8.00\n"),
        ("3\nSun\nyes\n", "Ticket: free\nPrice: $0.00\n"),
    ]:
        printed = run(typed)
        assert printed == expected, (
            f"Typing {typed.split()} should print:\n{expected}Your program printed:\n{printed}"
        )
