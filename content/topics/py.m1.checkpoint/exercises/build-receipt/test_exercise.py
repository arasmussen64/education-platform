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

TYPED = "18\n4\n20\n"
DECIMALS = "12.25\n3.5\n15\n"
OTHER = "16\n4\n15\n"


def test_subtotal():
    """Adds the meal and drinks, which may have decimals: 18 and 4 make 22.00, and 12.25 and 3.5 make 15.75."""
    assert close(amounts(TYPED).get("Subtotal"), 22)
    assert close(amounts(DECIMALS).get("Subtotal"), 15.75)


def test_tip():
    """Works out the tip as a percentage of the subtotal: 20% of 22.00 is 4.40."""
    for typed, percent in [(TYPED, 20), (OTHER, 15)]:
        found = amounts(typed)
        assert "Subtotal" in found
        assert close(found.get("Tip"), found["Subtotal"] * percent / 100)


def test_total():
    """Adds the tip to the subtotal: 22.00 and 4.40 make 26.40."""
    found = amounts(TYPED)
    assert "Subtotal" in found and "Tip" in found
    assert close(found.get("Total"), found["Subtotal"] + found["Tip"])


def test_tip_percent():
    """Shows the tip percentage as a whole number: Tip (20%)."""
    assert "Tip (20%)" in run(TYPED)


def test_two_decimals():
    """Shows every amount with two decimal places, like $4.40."""
    assert two_decimals(run(TYPED), 3)


def test_layout():
    """Prints three lines with the same words, spaces and $ signs as the example."""
    assert layout(run(TYPED)) == "Subtotal: $N\nTip (N%): $N\nTotal: $N\n"
