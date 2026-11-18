from checks import function, run, run_with

TABLE = (
    "2%: rule 36.0, exact 35.0\n"
    "6%: rule 12.0, exact 11.9\n"
    "10%: rule 7.2, exact 7.3\n"
    "24%: rule 3.0, exact 3.2\n"
)


def test_rule_of_72():
    """rule_of_72(0.09) is 8 years, and rule_of_72(0.04) is 18."""
    rule_of_72 = function("rule_of_72")
    assert abs(rule_of_72(0.09) - 8) < 1e-9, f"rule_of_72(0.09) returned {rule_of_72(0.09)}"
    assert abs(rule_of_72(0.04) - 18) < 1e-9, f"rule_of_72(0.04) returned {rule_of_72(0.04)}"


def test_doubling_time():
    """doubling_time(0.07) is about 10.24 years, and doubling_time(1.0) is exactly 1."""
    doubling_time = function("doubling_time")
    assert abs(doubling_time(0.07) - 10.2448) < 0.001, (
        f"doubling_time(0.07) returned {doubling_time(0.07)}"
    )
    assert abs(doubling_time(1.0) - 1) < 1e-9, f"doubling_time(1.0) returned {doubling_time(1.0)}"


def test_the_table():
    """Prints the four rows, from 2% to 24%."""
    printed = run()
    assert printed == TABLE, f"Expected this:\n{TABLE}\nYour program printed:\n{printed}"


def test_other_rates():
    """Works for another list: 3% and 12% print rule 24.0, exact 23.4 and rule 6.0, exact 6.1."""
    expected = "3%: rule 24.0, exact 23.4\n12%: rule 6.0, exact 6.1\n"
    printed = run_with({"rates": [0.03, 0.12]})
    assert printed == expected, (
        f"With rates = [0.03, 0.12] it should print:\n{expected}\nIt printed:\n{printed}"
    )
