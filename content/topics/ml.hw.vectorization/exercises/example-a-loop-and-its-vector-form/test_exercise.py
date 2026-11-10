import re

from checks import run

EXACT = {0: 'the loop and X @ w agree: True', 1: 'w stretched to (2000, 8) has strides (0, 8) | (X * w).sum(axis=1) agrees with X @ w: True', 2: 'the loop asks the interpreter for 16,000 multiplications and 16,000 additions, one at a time; X @ w asks once', 6: 'the moving average: 2,000 steps that each need the last, so 2,000 vector operations instead of 16,000 scalar ones', 7: 'a running total has a library form, np.cumsum: True'}
# The timing lines differ by machine and by clock, so they are checked by shape.
SHAPES = {3: 'loop: [0-9]+\\.[0-9] ms for 2,000 rows, [0-9]+\\.[0-9] ms for 4,000; ratio (?:[0-9]+\\.[0-9]|n/a)', 4: 'X @ w: [0-9]+\\.[0-9]{3} ms for 2,000 rows, [0-9]+\\.[0-9]{3} ms for 4,000; ratio (?:[0-9]+\\.[0-9]|n/a)', 5: 'at 4,000 rows the vectorized form is (?:[0-9]+\\.[0-9]|n/a) times faster'}


def test_the_walkthrough():
    """Prints the agreement, the broadcast, the counts, three timing lines in the right shape, and the moving average."""
    lines = run().splitlines()
    assert len(lines) == 8, lines
    for i, text in EXACT.items():
        assert lines[i] == text, lines[i]
    for i, pattern in SHAPES.items():
        assert re.fullmatch(pattern, lines[i]), lines[i]
