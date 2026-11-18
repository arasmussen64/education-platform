from checks import run, run_with


def test_the_offer():
    """At 5% the later offer is worth 7,774.54 today, so the money now wins."""
    expected = "The later offer, today: 7,774.54\nTake the money now\n"
    printed = run()
    assert printed == expected, f"Expected this:\n{expected}\nYour program printed:\n{printed}"


def test_a_lower_rate():
    """At 2% the later offer is worth 8,480.90 today, so it wins."""
    expected = "The later offer, today: 8,480.90\nTake the later offer\n"
    printed = run_with({"rate": 0.02})
    assert printed == expected, (
        f"With rate = 0.02 it should print:\n{expected}\nIt printed:\n{printed}"
    )
