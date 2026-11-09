import math

STAYS = [30, 90, 61, 600, 0]


def hours_started(minutes):
    """Return how many hours have been started."""
    return math.ceil(minutes / 60)


def fee(minutes):
    """Return the fee for a stay."""
    hours = hours_started(minutes)
    if hours == 0:
        return 0.0
    return min(12.0, 2.0 + 1.5 * (hours - 1))


def report_lines(stays):
    """Return one line per stay, then the total."""
    lines = []
    total = 0
    for minutes in stays:
        cost = fee(minutes)
        total += cost
        lines.append(f"{minutes} min: {cost:.2f}")
    lines.append(f"Total: {total:.2f}")
    return lines


def test_parking():
    assert hours_started(0) == 0
    assert hours_started(61) == 2
    print("parking: all checks passed")


def main():
    """Print the report."""
    for line in report_lines(STAYS):
        print(line)


if __name__ == "__main__":
    test_parking()
    main()
