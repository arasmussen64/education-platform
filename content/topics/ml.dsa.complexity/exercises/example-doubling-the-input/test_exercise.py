import re

from checks import run


def test_the_walkthrough():
    """Prints the exact step counts, and timing ratios within the noise (near 4, and well above 20)."""
    lines = run().splitlines()
    assert lines[:4] == ['500 slow 124750 fast 500', '1000 slow 499500 fast 1000', '2000 slow 1999000 fast 2000', 'steps from 1000 to 2000: slow x 4.0 fast x 2.0'], lines
    ratio = float(re.search(r"slow x ([\d.]+)", lines[4]).group(1))
    assert 2.5 <= ratio <= 6.5, lines[4]
    times = int(re.search(r"takes (\d+) times", lines[5]).group(1))
    assert times >= 20, lines[5]
