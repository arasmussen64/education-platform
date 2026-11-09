from checks import function

# Hidden tests: in a review, the learner sees each docstring and whether it
# passed, but not the failure messages.


def test_ordinary_cases():
    """120 pays 108.0, 60 pays 57.0, and 20 pays 20."""
    amount_to_pay = function("amount_to_pay")
    assert amount_to_pay(120) == 108.0
    assert amount_to_pay(60) == 57.0
    assert amount_to_pay(20) == 20


def test_boundaries_and_rounding():
    """100 and 50 get the discount, 99.99 and 49.99 get the smaller one or none, and 66.66 pays 63.33."""
    amount_to_pay = function("amount_to_pay")
    assert amount_to_pay(100) == 90.0
    assert amount_to_pay(99.99) == 94.99
    assert amount_to_pay(50) == 47.5
    assert amount_to_pay(49.99) == 49.99
    assert amount_to_pay(66.66) == 63.33
