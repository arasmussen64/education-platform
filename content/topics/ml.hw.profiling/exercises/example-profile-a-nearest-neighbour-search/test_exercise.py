import re

from checks import run

EXACT = {0: 'distance_squared: 30,000 calls | nearest: 1 call | list.append: 100 calls', 2: 'doubling both inputs: 120,000 calls, 4.0 times as many: the loop is quadratic', 3: 'vectorized: 0 calls to distance_squared, same answers: True'}
# The share and the byte counts vary by machine, so those lines are checked by shape.
SHAPES = {1: "distance_squared's own time is [0-9]+% of the profiled total", 4: 'a list of 100,000 floats: [0-9,]+ bytes at peak \\| the array: 800,000 bytes \\| the list took [0-9]+\\.[0-9] times as much'}


def test_the_walkthrough():
    """Prints the counts, a share, the doubling test, the vectorized profile and the memory comparison."""
    lines = run().splitlines()
    assert len(lines) == 5, lines
    for i, text in EXACT.items():
        assert lines[i] == text, lines[i]
    for i, pattern in SHAPES.items():
        assert re.fullmatch(pattern, lines[i]), lines[i]
