import math

from checks import function, run


def test_the_output():
    """Prints the same three probabilities twice."""
    assert run() == '[0.09, 0.2447, 0.6652]\n[0.09, 0.2447, 0.6652]\n'


def test_sums_and_survives():
    """Sums to 1 for ordinary, huge and very negative inputs."""
    softmax = function("softmax")
    for xs in ([0.0, 0.0], [5000.0, 4000.0], [-5000.0, -5001.0]):
        assert math.isclose(sum(softmax(xs)), 1.0)
