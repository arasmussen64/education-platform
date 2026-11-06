from checks import run, run_with


def test_twenty_five():
    """Prints 77.0 for 25 degrees Celsius."""
    printed = run()
    assert printed == "77.0\n", f"Expected 77.0. Your program printed:\n{printed}"


def test_other_temperatures():
    """Works for other temperatures: 100 becomes 212.0, and -40 stays -40.0."""
    for celsius, expected in [(100, "212.0\n"), (-40, "-40.0\n")]:
        printed = run_with({"celsius": celsius})
        assert printed == expected, (
            f"With celsius = {celsius} it should print {expected.strip()}. "
            f"It printed:\n{printed}"
        )
