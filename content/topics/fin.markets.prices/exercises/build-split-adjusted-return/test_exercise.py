from checks import function, run, run_with

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).

EXPECTED = (
    "day 0: 60.00\n"
    "day 1: 62.00\n"
    "day 2: 65.00\n"
    "day 3: 66.00\n"
    "day 4: 67.50\n"
    "day 5: 69.00\n"
    "return from the raw closes: -42.5%\n"
    "true return: 15.0%\n"
)


def test_the_report():
    """Prints the six adjusted closes, the return from the raw closes, and the true return."""
    assert run() == EXPECTED


def test_adjust_another_split():
    """adjust_for_split handles a 3-for-1 split on another day."""
    adjust_for_split = function("adjust_for_split")
    assert adjust_for_split([90.0, 93.0, 31.5, 32.0], 2, 3) == [30.0, 31.0, 31.5, 32.0]
    assert adjust_for_split([40.0, 11.0, 10.5], 1, 4) == [10.0, 11.0, 10.5]


def test_leaves_the_closes_alone():
    """adjust_for_split returns a new list and leaves the raw closes as they were."""
    adjust_for_split = function("adjust_for_split")
    raw = [90.0, 93.0, 31.5, 32.0]
    adjust_for_split(raw, 2, 3)
    assert raw == [90.0, 93.0, 31.5, 32.0]


def test_total_return():
    """total_return is the last price over the first, minus 1."""
    total_return = function("total_return")
    assert abs(total_return([30.0, 31.0, 31.5, 33.0]) - 0.1) < 1e-9
    assert abs(total_return([50.0, 40.0]) - (-0.2)) < 1e-9


def test_other_history():
    """The report works for another history, split and ratio too."""
    printed = run_with({"closes": [40.0, 11.0, 10.5, 12.0], "split_day": 1, "ratio": 4})
    assert printed == (
        "day 0: 10.00\n"
        "day 1: 11.00\n"
        "day 2: 10.50\n"
        "day 3: 12.00\n"
        "return from the raw closes: -70.0%\n"
        "true return: 20.0%\n"
    )
