from checks import run


def test_the_walkthrough():
    """Prints the loss curve, the accuracy and the classes."""
    assert run() == 'loss 0.732 0.017 0.001\naccuracy 1.0\nclasses [0 1 1 0]\n'
