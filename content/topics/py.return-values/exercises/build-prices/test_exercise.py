from checks import function, printed, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).


def test_total_price():
    """total_price(4, 3) returns 12, and total_price(2.5, 2) returns 5.0."""
    total_price = function("total_price")
    assert total_price(4, 3) == 12
    assert total_price(2.5, 2) == 5.0


def test_with_tax():
    """with_tax(10) returns 11.0, and with_tax(12) returns 13.2."""
    with_tax = function("with_tax")
    assert with_tax(10) == 11.0
    assert with_tax(12) == 13.2


def test_returns_not_prints():
    """Both functions return their result instead of printing it."""
    assert printed(function("total_price"), 4, 3) == ""
    assert printed(function("with_tax"), 10) == ""


def test_combined():
    """with_tax(total_price(4, 3)) is 13.2: one result feeds the other."""
    assert function("with_tax")(function("total_price")(4, 3)) == 13.2


def test_program():
    """Running the program prints Total: $13.20."""
    assert run() == "Total: $13.20\n"
