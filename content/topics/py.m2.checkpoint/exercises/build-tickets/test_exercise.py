import re

from checks import run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7). Each test checks one part of the
# program, so a failure points at the skill behind it (test_skills in
# exercise.yaml, ADR-0012).


def ticket(age, day, member):
    """The kind of ticket and the price the program printed, whatever the
    format: ("child", 8.0). Missing parts come back as None."""
    printed = run(f"{age}\n{day}\n{member}\n")
    kind = re.search(r"Ticket:\s*(\w+)", printed)
    price = re.search(r"Price:\s*\$?\s*(\d+(?:\.\d+)?)", printed)
    return (
        kind.group(1) if kind else None,
        float(price.group(1)) if price else None,
    )


def close(amount, expected):
    """Whether the amount was printed, and is right to the cent."""
    return amount is not None and abs(amount - expected) < 0.01


def test_adult():
    """An adult on a weekday pays $12.00: Ticket: adult."""
    kind, price = ticket(30, "Mon", "no")
    assert kind == "adult"
    assert close(price, 12)


def test_child_and_free():
    """Under 5 is free; 5 to 12 is a child at $6.00; 13 is an adult."""
    assert ticket(3, "Mon", "no") == ("free", 0)
    assert ticket(10, "Mon", "no") == ("child", 6)
    assert ticket(5, "Mon", "no") == ("child", 6)
    assert ticket(12, "Mon", "no") == ("child", 6)
    assert ticket(13, "Mon", "no")[0] == "adult"


def test_senior():
    """65 and over is a senior at $8.00; 64 is an adult."""
    assert ticket(70, "Mon", "no") == ("senior", 8)
    assert ticket(65, "Mon", "no") == ("senior", 8)
    assert ticket(64, "Mon", "no")[0] == "adult"


def test_weekend():
    """Sat and Sun add $2.00, but a free ticket stays free, and Mon adds nothing."""
    assert close(ticket(30, "Sat", "no")[1], 14)
    assert close(ticket(30, "Sun", "no")[1], 14)
    assert close(ticket(10, "Sat", "no")[1], 8)
    assert close(ticket(3, "Sat", "no")[1], 0)
    assert close(ticket(30, "Mon", "no")[1], 12)


def test_member():
    """Members pay 90%, worked out after the weekend extra: $10.80, or $12.60 on a Saturday."""
    assert close(ticket(30, "Mon", "yes")[1], 10.8)
    assert close(ticket(30, "Sat", "yes")[1], 12.6)
    assert close(ticket(12, "Mon", "yes")[1], 5.4)


def test_two_decimals():
    """Shows the price with a $ and two decimal places, like $8.00."""
    for typed in ("10\nSat\nno\n", "30\nMon\nyes\n", "3\nMon\nno\n"):
        assert re.search(r"\$\d+\.\d\d(?:\n|$)", run(typed))


def test_layout():
    """Prints two lines, Ticket: and Price:, with the same words as the example."""
    printed = re.sub(r"\d+(?:\.\d+)?", "N", run("10\nSat\nno\n"))
    assert printed == "Ticket: child\nPrice: $N\n"
