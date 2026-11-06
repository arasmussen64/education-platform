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

TYPED = "350\n0.24\n5\n"
DECIMALS = "512.5\n0.3\n8\n"
OTHER = "400\n0.25\n8\n"


def test_energy():
    """Works out the energy cost: 350 kWh at $0.24 is 84.00 (and 512.5 at $0.30 is 153.75)."""
    assert close(amounts(TYPED).get("Energy"), 84)
    assert close(amounts(DECIMALS).get("Energy"), 153.75)


def test_tax():
    """Works out the tax as a percentage of the energy cost: 5% of 84.00 is 4.20."""
    for typed, percent in [(TYPED, 5), (OTHER, 8)]:
        found = amounts(typed)
        assert "Energy" in found
        assert close(found.get("Tax"), found["Energy"] * percent / 100)


def test_total():
    """Adds the tax to the energy cost: 84.00 and 4.20 make 88.20."""
    found = amounts(TYPED)
    assert "Energy" in found and "Tax" in found
    assert close(found.get("Total"), found["Energy"] + found["Tax"])


def test_tax_percent():
    """Shows the tax percentage as a whole number: Tax (5%)."""
    assert "Tax (5%)" in run(TYPED)


def test_two_decimals():
    """Shows every amount with two decimal places, like $4.20."""
    assert two_decimals(run(TYPED), 3)


def test_layout():
    """Prints three lines with the same words, spaces and $ signs as the example."""
    assert layout(run(TYPED)) == "Energy: $N\nTax (N%): $N\nTotal: $N\n"
