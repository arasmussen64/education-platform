import re

from checks import run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7). Each test checks one part of the
# program, so a failure points at the skill behind it (test_skills in
# exercise.yaml, ADR-0012).


def ticket(age, session, card):
    """The kind of ticket and the price the program printed, whatever the
    format: ("adult", 4.8). Missing parts come back as None."""
    printed = run(f"{age}\n{session}\n{card}\n")
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
    """An adult in the morning without a card pays $5.00: Ticket: adult."""
    kind, price = ticket(30, "morning", "no")
    assert kind == "adult"
    assert close(price, 5)


def test_child_and_free():
    """Under 3 is free; 3 to 15 is a child at $3.00; 16 is an adult."""
    assert ticket(2, "morning", "no") == ("free", 0)
    assert ticket(10, "morning", "no") == ("child", 3)
    assert ticket(3, "morning", "no") == ("child", 3)
    assert ticket(15, "morning", "no") == ("child", 3)
    assert ticket(16, "morning", "no")[0] == "adult"


def test_senior():
    """60 and over is a senior at $3.50; 59 is an adult."""
    assert ticket(65, "morning", "no") == ("senior", 3.5)
    assert ticket(60, "morning", "no") == ("senior", 3.5)
    assert ticket(59, "morning", "no")[0] == "adult"


def test_evening():
    """Evenings add $1.00, but a free ticket stays free, and afternoons add nothing."""
    assert close(ticket(30, "evening", "no")[1], 6)
    assert close(ticket(10, "evening", "no")[1], 4)
    assert close(ticket(2, "evening", "no")[1], 0)
    assert close(ticket(30, "afternoon", "no")[1], 5)


def test_card():
    """Card holders pay 80%, worked out after the evening extra: $4.00, or $4.80 in the evening."""
    assert close(ticket(30, "morning", "yes")[1], 4)
    assert close(ticket(30, "evening", "yes")[1], 4.8)
    assert close(ticket(65, "morning", "yes")[1], 2.8)


def test_two_decimals():
    """Shows the price with a $ and two decimal places, like $4.80."""
    for typed in ("30\nevening\nyes\n", "10\nmorning\nno\n", "2\nmorning\nno\n"):
        assert re.search(r"\$\d+\.\d\d(?:\n|$)", run(typed))


def test_layout():
    """Prints two lines, Ticket: and Price:, with the same words as the example."""
    printed = re.sub(r"\d+(?:\.\d+)?", "N", run("30\nevening\nyes\n"))
    assert printed == "Ticket: adult\nPrice: $N\n"
