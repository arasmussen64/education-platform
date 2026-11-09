import re

from checks import run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7). Each test checks one part of the
# program, so a failure points at the skill behind it (test_skills in
# exercise.yaml, ADR-0012).


def journey(distance, time, railcard):
    """The kind of journey and the fare the program printed, whatever the
    format: ("medium", 7.5). Missing parts come back as None."""
    printed = run(f"{distance}\n{time}\n{railcard}\n")
    kind = re.search(r"Journey:\s*(\w+)", printed)
    fare = re.search(r"Fare:\s*\$?\s*(\d+(?:\.\d+)?)", printed)
    return (
        kind.group(1) if kind else None,
        float(fare.group(1)) if fare else None,
    )


def close(amount, expected):
    """Whether the amount was printed, and is right to the cent."""
    return amount is not None and abs(amount - expected) < 0.01


def test_medium():
    """30 km off-peak without a railcard is a medium journey at $6.00."""
    kind, fare = journey(30, "offpeak", "no")
    assert kind == "medium"
    assert close(fare, 6)


def test_short_and_long():
    """Up to 10 km is short at $2.50, over 50 km is long at $15.00, and the boundaries count down."""
    assert journey(5, "offpeak", "no") == ("short", 2.5)
    assert journey(10, "offpeak", "no") == ("short", 2.5)
    assert journey(10.5, "offpeak", "no")[0] == "medium"
    assert journey(50, "offpeak", "no") == ("medium", 6)
    assert journey(100, "offpeak", "no") == ("long", 15)


def test_peak():
    """Peak adds $1.50 to every journey; off-peak adds nothing."""
    assert close(journey(30, "peak", "no")[1], 7.5)
    assert close(journey(5, "peak", "no")[1], 4)
    assert close(journey(100, "offpeak", "no")[1], 15)


def test_railcard():
    """A railcard takes a third off, after the peak extra: $5.00 for 30 km at peak, $11.00 for 100 km at peak."""
    assert close(journey(30, "peak", "yes")[1], 5)
    assert close(journey(100, "peak", "yes")[1], 11)
    assert close(journey(5, "offpeak", "yes")[1], 1.67)


def test_two_decimals():
    """Shows the fare with a $ and two decimal places, like $7.50."""
    for typed in ("30\npeak\nno\n", "5\noffpeak\nyes\n", "100\noffpeak\nno\n"):
        assert re.search(r"\$\d+\.\d\d(?:\n|$)", run(typed))


def test_layout():
    """Prints two lines, Journey: and Fare:, with the same words as the example."""
    printed = re.sub(r"\d+(?:\.\d+)?", "N", run("30\npeak\nno\n"))
    assert printed == "Journey: medium\nFare: $N\n"
