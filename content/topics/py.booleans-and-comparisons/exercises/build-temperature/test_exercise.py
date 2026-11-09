from checks import run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).


def test_below_zero():
    """Typing -2.5 prints Below zero: True, Above 30: False, Exactly 20: False."""
    assert run("-2.5\n") == "Below zero: True\nAbove 30: False\nExactly 20: False\n"


def test_exactly_twenty():
    """Typing 20 prints Below zero: False, Above 30: False, Exactly 20: True."""
    assert run("20\n") == "Below zero: False\nAbove 30: False\nExactly 20: True\n"


def test_thirty_is_not_above_thirty():
    """Typing 30 prints Above 30: False, because 30 is not above 30."""
    assert run("30\n") == "Below zero: False\nAbove 30: False\nExactly 20: False\n"


def test_hot_with_decimals():
    """Typing 35.5 prints Below zero: False, Above 30: True, Exactly 20: False."""
    assert run("35.5\n") == "Below zero: False\nAbove 30: True\nExactly 20: False\n"
