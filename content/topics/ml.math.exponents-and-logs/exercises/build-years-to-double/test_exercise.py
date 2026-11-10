from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).


def test_the_table():
    """Prints the years to double at 2%, 5% and 10%."""
    assert run() == "2%: 36 years\n5%: 15 years\n10%: 8 years\n"


def test_the_function():
    """years_to_double(100) is 1, and years_to_double(7) is 11."""
    years_to_double = function("years_to_double")
    assert years_to_double(100) == 1
    assert years_to_double(7) == 11
