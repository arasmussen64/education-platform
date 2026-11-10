import numpy as np

from checks import function, run


def test_the_output():
    """Prints the belief after ten flips, its peak and the peak's probability."""
    printed = run()
    assert printed == '[0.    0.214 0.333 0.258 0.133 0.048 0.012 0.002 0.    0.    0.   ]\n0.2 0.333\n', f"Your program printed:\n{printed}"


def test_one_update():
    """A flat belief over three candidates updated with likelihoods [0.2, 0.3, 0.5] becomes those numbers; a second heads doubles down."""
    update = function("update")
    belief = update(np.array([1 / 3, 1 / 3, 1 / 3]), np.array([0.2, 0.3, 0.5]))
    assert np.allclose(belief, [0.2, 0.3, 0.5])
    assert abs(belief.sum() - 1) < 1e-12
    again = update(belief, np.array([0.2, 0.3, 0.5]))
    assert np.allclose(again, np.array([0.04, 0.09, 0.25]) / 0.38)
