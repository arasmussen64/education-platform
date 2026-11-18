from checks import function, run, run_with

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).

TABLE = (
    "Year 0: 1,500.00\n"
    "Year 1: 1,552.50\n"
    "Year 2: 1,606.84\n"
    "Year 3: 1,663.08\n"
    "Year 4: 1,721.28\n"
)


def test_the_function():
    """future_value(2500, 0.04, 10) is 3,700.61 to the cent, and 100 at 10% for 2 periods is 121."""
    future_value = function("future_value")
    assert abs(future_value(2500, 0.04, 10) - 3700.61) < 0.005
    assert abs(future_value(100, 0.1, 2) - 121) < 0.005


def test_no_periods():
    """After 0 periods an amount is still what it was: future_value(750, 0.05, 0) is 750."""
    future_value = function("future_value")
    assert abs(future_value(750, 0.05, 0) - 750) < 0.005


def test_the_table():
    """Prints the five rows, from Year 0: 1,500.00 to Year 4: 1,721.28."""
    assert run() == TABLE


def test_other_starting_values():
    """Works for other starting values: 20,000 at 8% for 3 years ends at 25,194.24."""
    expected = (
        "Year 0: 20,000.00\nYear 1: 21,600.00\nYear 2: 23,328.00\nYear 3: 25,194.24\n"
    )
    assert run_with({"present": 20000, "rate": 0.08, "years": 3}) == expected
