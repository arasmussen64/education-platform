from checks import run, run_with

EXPECTED = "Ada Grace\nGrace Ada\n"


def test_seats():
    """Prints Ada Grace, then Grace Ada."""
    printed = run()
    assert printed == EXPECTED, (
        f"Expected this:\n{EXPECTED}\nYour program printed:\n{printed}"
    )


def test_swaps_any_values():
    """Swaps any two people, not just Ada and Grace."""
    printed = run_with({"left": "Mo", "right": "Jo"})
    assert printed == "Mo Jo\nJo Mo\n", (
        "Starting with Mo on the left and Jo on the right, it should print "
        f"Mo Jo, then Jo Mo. It printed:\n{printed}"
    )
