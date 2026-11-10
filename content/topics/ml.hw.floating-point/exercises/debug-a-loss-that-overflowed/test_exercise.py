import math

from checks import function, run

EXPECTED = 'losses: [0.417, 0.4076, 1.0986] mean: 0.6411\nprobabilities sum to 1: True\n'


def test_the_output():
    """Prints the three losses, their mean and a True."""
    printed = run()
    assert printed == EXPECTED, f"Expected this:\n{EXPECTED}\nYour program printed:\n{printed}"


def test_large_logits():
    """softmax survives logits of 5,000 and the loss of a confident right answer is near 0."""
    softmax = function("softmax")
    cross_entropy = function("cross_entropy")
    assert math.isclose(sum(softmax([5000.0, 4999.0, 4990.0])), 1.0)
    assert cross_entropy([50.0, 0.0, 0.0], 0) < 1e-10
