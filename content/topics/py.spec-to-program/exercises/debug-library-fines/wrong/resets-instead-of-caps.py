# Spec: A library charges 0.25 for each day a book is late, but the first
# three late days are free, and a fine is never more than 5.00. A book
# returned on time, or early, has no fine. Print each fine with two decimals.

DAYS_LATE = [1, 10, 40, -1]


def fine(days_late):
    """Return the fine for a book this many days late, following the spec."""
    chargeable = days_late - 3
    if chargeable < 0:
        chargeable = 0
    fine_due = 0.25 * chargeable
    if fine_due > 5.0:
        fine_due = 0.0
    return fine_due


def main():
    """Print one line per book."""
    for days in DAYS_LATE:
        print(f"Days late: {days}, fine: {fine(days):.2f}")


if __name__ == "__main__":
    main()
