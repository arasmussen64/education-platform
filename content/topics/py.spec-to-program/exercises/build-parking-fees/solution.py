import math

# Examples from the spec: 0 min -> 0.00; 1 to 60 min -> 2.00; 61 min -> 3.50;
# 420 min -> 11.00; 421 min and anything longer -> 12.00, the daily maximum.

STAYS = [30, 90, 61, 600, 0]


def hours_started(minutes):
    """Return how many hours have been started: 0 for 0, 1 for 1 to 60, and so on."""
    return math.ceil(minutes / 60)


def fee(minutes):
    """Return the fee for a stay: 2.00 for the first hour, 1.50 per extra, at most 12.00."""
    hours = hours_started(minutes)
    if hours == 0:
        return 0.0
    return min(12.0, 2.0 + 1.5 * (hours - 1))


def report_lines(stays):
    """Return one line per stay, like '90 min: 3.50', then the total."""
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
    assert hours_started(60) == 1
    assert hours_started(61) == 2
    assert fee(0) == 0.0
    assert fee(60) == 2.0
    assert fee(61) == 3.5
    assert fee(600) == 12.0
    assert report_lines([30]) == ["30 min: 2.00", "Total: 2.00"]
    print("parking: all checks passed")


def main():
    """Print the report for the day's stays."""
    for line in report_lines(STAYS):
        print(line)


if __name__ == "__main__":
    test_parking()
    main()
