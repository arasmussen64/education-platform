import re

from checks import run

TYPED = "2\n3\n12.5\n"
OTHER = "1\n2\n9\n"


def total_line(printed):
    """The line that starts with Total, or an empty one."""
    lines = [line for line in printed.splitlines() if line.startswith("Total")]
    return lines[0] if lines else ""


def test_counts_tickets():
    """Counts the tickets: 2 adults and 3 children make Tickets: 5."""
    printed = run(TYPED)
    assert "Tickets: 5" in printed.splitlines(), f"Your program printed:\n{printed}"


def test_children_pay_half():
    """Children pay half price: 2 adults and 3 children at 12.5 come to 43.75."""
    printed = run(TYPED)
    number = re.search(r"\d+(?:\.\d+)?", total_line(printed).partition(":")[2])
    assert number and abs(float(number.group()) - 43.75) < 0.01, (
        f"Your program printed:\n{printed}"
    )


def test_total_line():
    """Shows the total with $ right before it and two decimal places, like Total: $43.75."""
    for typed in (TYPED, OTHER):
        printed = run(typed)
        assert re.fullmatch(r"Total: \$\d+\.\d\d", total_line(printed)), (
            f"Your program printed:\n{printed}"
        )
