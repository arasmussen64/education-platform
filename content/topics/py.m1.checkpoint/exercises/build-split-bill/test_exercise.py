import re

from checks import run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7). Each test checks one part of the
# program, so a failure points at the skill behind it (test_skills in
# exercise.yaml, ADR-0012).


def amounts(typed):
    """The number on each printed line, by the line's first word, whatever its
    format: "Tip (20%): $ 4.4" gives {"Tip": 4.4}."""
    found = {}
    for line in run(typed).splitlines():
        label, _, rest = line.partition(":")
        number = re.search(r"\d+(?:\.\d+)?", rest)
        if label.strip() and number:
            found[label.split()[0]] = float(number.group())
    return found


def close(amount, expected):
    """Whether the amount was printed, and is right to the cent (printed amounts
    are rounded). Missing lines fail the test instead of crashing it."""
    return amount is not None and abs(amount - expected) < 0.01


def two_decimals(text, count):
    """Whether the text shows `count` amounts after a $, each with exactly two
    decimal places, whatever their values."""
    shown = re.findall(r"\$\s*(\d+(?:\.\d+)?)", text)
    return len(shown) == count and all(re.fullmatch(r"\d+\.\d\d", a) for a in shown)


def layout(text):
    """The text with every number replaced by N: just the words and spaces."""
    return re.sub(r"\d+(?:\.\d+)?", "N", text)

TYPED = "60\n3\n15\n"
DECIMALS = "47.8\n4\n18\n"
OTHER = "80\n4\n10\n"


def test_bill():
    """Reads the bill, which may have decimals: Bill: $60.00, or $47.80."""
    assert close(amounts(TYPED).get("Bill"), 60)
    assert close(amounts(DECIMALS).get("Bill"), 47.8)


def test_tip():
    """Works out the tip as a percentage of the bill: 15% of 60.00 is 9.00."""
    for typed, percent in [(TYPED, 15), (OTHER, 10)]:
        found = amounts(typed)
        assert "Bill" in found
        assert close(found.get("Tip"), found["Bill"] * percent / 100)


def test_each_pays():
    """Splits the bill and tip evenly: 69.00 between 3 people is 23.00 each."""
    for typed, people in [(TYPED, 3), (OTHER, 4)]:
        found = amounts(typed)
        assert "Bill" in found and "Tip" in found
        assert close(found.get("Each"), (found["Bill"] + found["Tip"]) / people)


def test_whole_numbers():
    """Shows the tip percentage and the number of people as whole numbers."""
    printed = run(TYPED)
    assert "Tip (15%)" in printed
    assert "Each of 3 pays" in printed


def test_two_decimals():
    """Shows every amount with two decimal places, like $9.00."""
    assert two_decimals(run(TYPED), 3)


def test_layout():
    """Prints three lines with the same words, spaces and $ signs as the example."""
    assert layout(run(TYPED)) == "Bill: $N\nTip (N%): $N\nEach of N pays: $N\n"
