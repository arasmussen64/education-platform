import re

from checks import run


def test_the_walkthrough():
    """Prints the exact step counts, then two timing lines whose numbers depend on the machine and are not checked."""
    lines = run().splitlines()
    assert lines[:4] == ['500 slow 124750 fast 500', '1000 slow 499500 fast 1000', '2000 slow 1999000 fast 2000', 'steps from 1000 to 2000: slow x 4.0 fast x 2.0'], lines
    assert re.fullmatch(r"time from 800 to 1600: slow x [\d.]+", lines[4]), lines[4]
    assert re.fullmatch(r"at 1600, slow takes \d+ times longer than fast", lines[5]), lines[5]
