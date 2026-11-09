from checks import run


def test_child_on_a_saturday():
    """Typing 10, Sat and no prints Ticket: child and Price: $8.00."""
    printed = run("10\nSat\nno\n")
    assert printed == "Ticket: child\nPrice: $8.00\n", f"Your program printed:\n{printed}"


def test_weekday_and_weekend():
    """An adult pays $12.00 on Mon, $14.00 on Sun, and a free ticket stays free on Sat."""
    for typed, expected in [
        ("30\nMon\nno\n", "Ticket: adult\nPrice: $12.00\n"),
        ("30\nSun\nno\n", "Ticket: adult\nPrice: $14.00\n"),
        ("3\nSat\nno\n", "Ticket: free\nPrice: $0.00\n"),
    ]:
        printed = run(typed)
        assert printed == expected, (
            f"Typing {typed.split()} should print:\n{expected}Your program printed:\n{printed}"
        )


def test_members():
    """A member pays 90% after the weekend extra: $10.80 on Mon, $12.60 on Sat."""
    for typed, expected in [
        ("30\nMon\nyes\n", "Ticket: adult\nPrice: $10.80\n"),
        ("30\nSat\nyes\n", "Ticket: adult\nPrice: $12.60\n"),
    ]:
        printed = run(typed)
        assert printed == expected, (
            f"Typing {typed.split()} should print:\n{expected}Your program printed:\n{printed}"
        )
