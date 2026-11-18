from checks import run


def test_the_week():
    """Prints each day's move and range, the week as one bar, and the close-to-close returns."""
    assert run() == (
        "Mon: +1.00 from open to close, range 1.40\n"
        "Tue: -0.70 from open to close, range 1.30\n"
        "Wed: +3.20 from open to close, range 3.60\n"
        "Thu: -0.50 from open to close, range 1.30\n"
        "Fri: +0.40 from open to close, range 1.30\n"
        "week: open 50.00, high 54.00, low 49.80, close 53.20\n"
        "volume 766,000, busiest day Wed\n"
        "Tue: -1.18%\n"
        "Wed: +6.35%\n"
        "Thu: -1.12%\n"
        "Fri: +0.38%\n"
    )
