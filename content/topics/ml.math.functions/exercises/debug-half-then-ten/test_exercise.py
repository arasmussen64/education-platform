from checks import function, run

EXPECTED = "14.0\n1 10.5\n2 11.0\n3 11.5\n"


def test_the_output():
    """Prints 14.0, then the three rows of the table."""
    printed = run()
    assert printed == EXPECTED, (
        f"Expected this:\n{EXPECTED}\nYour program printed:\n{printed}"
    )


def test_half_of_an_odd_number():
    """half(5) is 2.5, not 2."""
    half = function("half")
    assert half(5) == 2.5, f"half(5) returned {half(5)}"
