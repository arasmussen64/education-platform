import re

from checks import run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7). Each test checks one part of the
# program, so a failure points at the skill behind it (test_skills in
# exercise.yaml, ADR-0012).


def stats(text):
    """The three statistics the program printed, whatever the format:
    (4, 27, 12). Missing parts come back as None."""
    printed = run(text + "\n")
    count = re.search(r"Numbers:\s*(\d+)", printed)
    total = re.search(r"Total:\s*(\d+)", printed)
    largest = re.search(r"Largest:\s*(\d+)", printed)
    return (
        int(count.group(1)) if count else None,
        int(total.group(1)) if total else None,
        int(largest.group(1)) if largest else None,
    )


def bars(text):
    """The lines of the chart: every printed line made only of #."""
    printed = run(text + "\n")
    return [line for line in printed.splitlines() if line and set(line) == {"#"}]


def test_count():
    """Counts the numbers: 4 in 12 7 3 5, 1 in 8."""
    assert stats("12 7 3 5")[0] == 4
    assert stats("8")[0] == 1


def test_total():
    """Adds them up as numbers: 27 for 12 7 3 5, 8 for 8."""
    assert stats("12 7 3 5")[1] == 27
    assert stats("8")[1] == 8
    assert stats("10 10")[1] == 20


def test_largest():
    """Finds the largest, wherever it is: 12 in 12 7 3 5, 9 in 3 9 4."""
    assert stats("12 7 3 5")[2] == 12
    assert stats("3 9 4")[2] == 9
    assert stats("8")[2] == 8


def test_last_number():
    """The last number counts too, even though no space follows it: 1 2 10 has 3 numbers and 10 is the largest."""
    assert stats("1 2 10")[0] == 3
    assert stats("1 2 10")[2] == 10
    assert stats("2 5")[2] == 5


def test_chart():
    """Draws one bar per number, with that many #, in order."""
    assert bars("3 1 2") == ["###", "#", "##"]
    assert bars("4") == ["####"]


def test_layout():
    """Prints exactly the three statistics lines and then the bars, as in the example."""
    assert run("12 7 3 5\n") == (
        "Numbers: 4\nTotal: 27\nLargest: 12\n############\n#######\n###\n#####\n"
    )
