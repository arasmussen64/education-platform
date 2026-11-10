import numpy as np

from checks import function, run

EXPECTED = 'plane [ 2.015 -1.035  3.024]\nloss 0.0063\n'


def test_the_output():
    """Prints the plane and its loss."""
    printed = run()
    assert printed == EXPECTED, f"Expected this:\n{EXPECTED}\nYour program printed:\n{printed}"


def test_loss_is_a_mean():
    """At the plane [2, -1, 4] (one unit too high everywhere) the loss is about 1 plus the floor, not six times that."""
    loss = function("loss")
    assert abs(float(loss(np.array([2.0, -1.0, 4.0]))) - float(loss(np.array([2.0, -1.0, 3.0]))) - 1.0) < 0.1


def test_gradient_shape():
    """The gradient has one entry per weight."""
    gradient = function("gradient")
    assert gradient(np.zeros(3)).shape == (3,)
