from checks import function, run, run_with

TABLE = "Year 0: 9,000.00\nYear 2: 9,070.29\nYear 4: 8,638.38\nBest: the offer in year 2\n"


def test_present_value():
    """present_value(1100, 0.1, 1) is 1,000, and 500 paid now is still 500."""
    present_value = function("present_value")
    assert abs(present_value(1100, 0.1, 1) - 1000) < 0.005, (
        f"present_value(1100, 0.1, 1) returned {present_value(1100, 0.1, 1)}"
    )
    assert abs(present_value(500, 0.07, 0) - 500) < 0.005, (
        f"present_value(500, 0.07, 0) returned {present_value(500, 0.07, 0)}"
    )


def test_the_table():
    """At 5%, the offer in year 2 is worth the most today."""
    printed = run()
    assert printed == TABLE, f"Expected this:\n{TABLE}\nYour program printed:\n{printed}"


def test_a_lower_rate():
    """At 1% the latest offer is worth the most: 10,090.29 today."""
    expected = (
        "Year 0: 9,000.00\nYear 2: 9,802.96\nYear 4: 10,090.29\n"
        "Best: the offer in year 4\n"
    )
    printed = run_with({"rate": 0.01})
    assert printed == expected, (
        f"With rate = 0.01 it should print:\n{expected}\nIt printed:\n{printed}"
    )
