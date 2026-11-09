from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).


def test_to_age():
    """to_age gives 34 for "34", 0 for "0", and None for "x", "3.5" and "-5"."""
    to_age = function("to_age")
    assert to_age("34") == 34
    assert to_age("0") == 0
    assert to_age("x") is None
    assert to_age("3.5") is None
    assert to_age("-5") is None


def test_valid_ages():
    """valid_ages keeps the valid ones in order and gives [] for none."""
    valid_ages = function("valid_ages")
    assert valid_ages(["34", "x", "-5", "7"]) == [34, 7]
    assert valid_ages(["a", "b"]) == []
    assert valid_ages([]) == []


def test_require_positive():
    """require_positive returns 3 for 3 and raises ValueError for 0 and -1."""
    require_positive = function("require_positive")
    assert require_positive(3) == 3
    for bad in (0, -1):
        raised = False
        try:
            require_positive(bad)
        except ValueError as error:
            raised = str(error) == "must be positive"
        assert raised


def test_program():
    """Running the program prints the valid ages and how many were skipped."""
    assert run() == "Valid ages: [34, 7]\nSkipped: 2\n"
