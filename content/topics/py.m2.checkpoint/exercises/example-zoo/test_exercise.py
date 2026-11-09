from checks import run


def test_child_on_a_saturday():
    """A child on a Saturday without a pass pays $12.00."""
    assert run("10\nSat\nno\n") == "Zoo ticket: child\nPrice: $12.00\n"


def test_adult_with_a_pass():
    """An adult with a pass on a Monday pays $12.00: 75% of $16."""
    assert run("30\nMon\nyes\n") == "Zoo ticket: adult\nPrice: $12.00\n"


def test_free_stays_free():
    """A toddler on a Sunday is still free."""
    assert run("2\nSun\nno\n") == "Zoo ticket: free\nPrice: $0.00\n"
