import numpy as np

from checks import function, run


def test_the_output():
    """Prints the clipped and the untouched list."""
    assert run() == '[[3.0, 0.0], [[4.0]]]\n[[6.0, 0.0], [[8.0]]]\n'


def test_other_cases():
    """A random list lands on the limit with its direction kept; a small one is returned as is."""
    clip_gradients = function("clip_gradients")
    rng = np.random.default_rng(3)
    grads = [rng.standard_normal(4), rng.standard_normal((2, 2))]
    norm = float(np.sqrt(sum((g ** 2).sum() for g in grads)))
    clipped = clip_gradients(grads, 0.25)
    assert abs(float(np.sqrt(sum((g ** 2).sum() for g in clipped))) - 0.25) < 1e-12
    assert np.allclose(clipped[0] / grads[0], clipped[1][0, 0] / grads[1][0, 0])
    assert clip_gradients(grads, norm * 2) is grads
