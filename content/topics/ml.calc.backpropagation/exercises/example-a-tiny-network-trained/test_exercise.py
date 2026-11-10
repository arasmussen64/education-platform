from checks import run


def test_the_walkthrough():
    """Prints the first predictions and loss, the gradient shapes, the check, the loss curve and the trained predictions."""
    assert run() == '[0.493 0.418 0.325 0.224] 0.732\n(2, 4) (4,) (4,)\nTrue\n0 0.732\n100 0.081\n500 0.004\n0.001 [0. 1. 1. 0.] 1.0\n'
