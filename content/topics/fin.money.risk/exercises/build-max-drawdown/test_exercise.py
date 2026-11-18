from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).


def matches(got, fall, start, end):
    return (
        isinstance(got, tuple)
        and len(got) == 3
        and isinstance(got[0], (int, float))
        and abs(got[0] - fall) < 1e-9
        and got[1] == start
        and got[2] == end
    )


def test_the_report():
    """Prints the fund's maximum drawdown and its two positions."""
    assert run() == "Maximum drawdown: 25.71%, from position 6 to position 8\n"


def test_simple_fall():
    """max_drawdown([10, 12, 9, 15, 6, 8]) is (0.6, 3, 4)."""
    max_drawdown = function("max_drawdown")
    assert matches(max_drawdown([10, 12, 9, 15, 6, 8]), 0.6, 3, 4)


def test_worst_fall_before_the_top():
    """In [100, 90, 95, 60, 100, 130, 91] the worst fall is 40%, from position 0 to 3, though 130 comes later."""
    max_drawdown = function("max_drawdown")
    assert matches(max_drawdown([100, 90, 95, 60, 100, 130, 91]), 0.4, 0, 3)
    assert matches(max_drawdown([40, 30, 45, 36, 44]), 0.25, 0, 1)


def test_never_falls():
    """A price that only rises has no drawdown: (0.0, 0, 0)."""
    max_drawdown = function("max_drawdown")
    assert matches(max_drawdown([5, 6, 7, 8]), 0.0, 0, 0)
