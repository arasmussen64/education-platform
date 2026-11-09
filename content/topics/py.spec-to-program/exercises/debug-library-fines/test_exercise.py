from checks import function, run


def test_free_days():
    """The first three late days are free: day 3 costs 0.00, day 4 costs 0.25, day 10 costs 1.75."""
    fine = function("fine")
    for days, expected in [(3, 0.0), (4, 0.25), (10, 1.75)]:
        got = fine(days)
        assert got == expected, f"fine({days}) returned {got!r}, not {expected!r}"


def test_maximum():
    """A fine is never more than 5.00: 23, 40 and 100 days all cost 5.00."""
    fine = function("fine")
    for days in (23, 40, 100):
        got = fine(days)
        assert got == 5.0, f"fine({days}) returned {got!r}, not 5.0"


def test_no_fine():
    """On time or early means no fine: 0, -1 and -10 days all cost 0.00, never a negative amount."""
    fine = function("fine")
    for days in (0, -1, -10, 1, 2):
        got = fine(days)
        assert got == 0.0, f"fine({days}) returned {got!r}, not 0.0"


def test_program():
    """Prints the four fines the spec gives for 1, 10, 40 and -1 days."""
    got = run()
    assert got == (
        "Days late: 1, fine: 0.00\nDays late: 10, fine: 1.75\n"
        "Days late: 40, fine: 5.00\nDays late: -1, fine: 0.00\n"
    ), f"Your program printed:\n{got}"
