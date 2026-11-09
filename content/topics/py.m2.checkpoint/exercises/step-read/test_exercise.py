from checks import run


def test_child_on_a_saturday():
    """Typing 10, Sat and no prints Ticket: child and Price: $8.00."""
    printed = run("10\nSat\nno\n")
    assert printed == "Ticket: child\nPrice: $8.00\n", f"Your program printed:\n{printed}"


def test_adult_member():
    """Typing 30, Mon and yes prints Ticket: adult and Price: $10.80."""
    printed = run("30\nMon\nyes\n")
    assert printed == "Ticket: adult\nPrice: $10.80\n", f"Your program printed:\n{printed}"


def test_senior_on_a_sunday():
    """Typing 70, Sun and no prints Ticket: senior and Price: $10.00."""
    printed = run("70\nSun\nno\n")
    assert printed == "Ticket: senior\nPrice: $10.00\n", f"Your program printed:\n{printed}"
